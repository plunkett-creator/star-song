package app.starsong

import android.app.Activity
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClient.BillingResponseCode
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import org.json.JSONArray
import org.json.JSONObject

/**
 * Google Play Billing for the Star Song bundle: one one-time product whose ID is
 * COLLECTION.bundleProductId in Web/pieces.js (starsong.bundle).
 * The collection page is told the price and what is owned through window.__storeUpdate.
 */
class Store(private val activity: Activity, private val send: (String) -> Unit) : PurchasesUpdatedListener {

    private val client: BillingClient = BillingClient.newBuilder(activity)
        .setListener(this)
        .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
        .enableAutoServiceReconnection()
        .build()

    private val details = mutableMapOf<String, ProductDetails>()
    private var owned = mutableSetOf<String>()
    private var wanted = listOf<String>()
    private var ready = false

    init {
        client.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(result: BillingResult) {
                ready = result.responseCode == BillingResponseCode.OK
                if (ready) {
                    queryDetails()
                    queryOwned(null)
                } else {
                    push("The store isn't available right now. Please check that Google Play is signed in.")
                }
            }

            override fun onBillingServiceDisconnected() {
                // Automatic reconnection is on, so nothing to do here.
            }
        })
    }

    /** The collection page asks for its products when it opens. */
    fun load(ids: List<String>) {
        wanted = ids
        if (ready) {
            queryDetails()
            queryOwned(null)
        } else {
            push(null)
        }
    }

    /** Re-check purchases when the app comes back to the front (e.g. a pending purchase was paid). */
    fun refresh() {
        if (ready) queryOwned(null)
    }

    fun buy(id: String) {
        val product = details[id]
        if (product == null) {
            push("The collection isn't available right now. Please check your connection and try again.")
            if (ready) queryDetails()
            return
        }
        val params = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(
                listOf(BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(product).build())
            )
            .build()
        val result = client.launchBillingFlow(activity, params)
        if (result.responseCode != BillingResponseCode.OK) {
            push("The purchase couldn't start. Please try again.")
        }
    }

    fun restore() {
        if (!ready) {
            push("The store isn't available right now. Please try again in a moment.")
            return
        }
        queryOwned { hasAny ->
            if (hasAny) "Your collection has been restored." else "No earlier purchases were found for this Google account."
        }
    }

    fun close() {
        try { client.endConnection() } catch (_: Exception) {}
    }

    override fun onPurchasesUpdated(result: BillingResult, purchases: MutableList<Purchase>?) {
        when (result.responseCode) {
            BillingResponseCode.OK -> {
                var pending = false
                purchases?.forEach { p ->
                    if (p.purchaseState == Purchase.PurchaseState.PURCHASED) {
                        owned.addAll(p.products)
                        acknowledge(p)
                    } else if (p.purchaseState == Purchase.PurchaseState.PENDING) {
                        pending = true
                    }
                }
                push(if (pending) "Your purchase is waiting for payment to go through." else "Thank you! The Star Song collection is now yours.")
            }
            BillingResponseCode.USER_CANCELED -> push(null)
            BillingResponseCode.ITEM_ALREADY_OWNED -> queryOwned { "You already own the collection, so it's been unlocked." }
            else -> push("The purchase didn't go through. Please try again.")
        }
    }

    private fun queryDetails() {
        if (wanted.isEmpty()) {
            push(null)
            return
        }
        val products = wanted.map {
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(it)
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        }
        val params = QueryProductDetailsParams.newBuilder().setProductList(products).build()
        client.queryProductDetailsAsync(params) { result, detailsResult ->
            if (result.responseCode == BillingResponseCode.OK) {
                for (d in detailsResult.productDetailsList) details[d.productId] = d
            }
            push(null)
        }
    }

    private fun queryOwned(message: ((Boolean) -> String?)?) {
        val params = QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()
        client.queryPurchasesAsync(params) { result, purchases ->
            if (result.responseCode == BillingResponseCode.OK) {
                val now = mutableSetOf<String>()
                for (p in purchases) {
                    if (p.purchaseState == Purchase.PurchaseState.PURCHASED) {
                        now.addAll(p.products)
                        acknowledge(p)
                    }
                }
                owned = now
            }
            push(message?.invoke(owned.isNotEmpty()))
        }
    }

    /** Google refunds purchases that aren't acknowledged within three days. */
    private fun acknowledge(p: Purchase) {
        if (p.isAcknowledged) return
        val params = AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.purchaseToken).build()
        client.acknowledgePurchase(params) { }
    }

    @Suppress("DEPRECATION")
    private fun priceOf(d: ProductDetails): String? = d.oneTimePurchaseOfferDetails?.formattedPrice

    private fun push(message: String?) {
        val prices = JSONObject()
        for ((id, d) in details) priceOf(d)?.let { prices.put(id, it) }
        val payload = JSONObject()
            .put("prices", prices)
            .put("owned", JSONArray(owned.toList()))
        if (message != null) payload.put("message", message)
        send("window.__storeUpdate && window.__storeUpdate($payload);")
    }
}
