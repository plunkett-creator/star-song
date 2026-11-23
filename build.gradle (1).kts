// Star Song for Android. The cloud build passes the package name, build number and signing key
// (see .github/workflows/android.yml); the pieces themselves come straight from ../../Web.
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

val appId = (findProperty("appId") as String?) ?: "com.example.starsong"
val buildNumber = ((findProperty("buildNumber") as String?) ?: "1").toInt()

android {
    namespace = "app.starsong"
    compileSdk = 36

    defaultConfig {
        applicationId = appId
        minSdk = 26
        targetSdk = 36
        versionCode = buildNumber
        versionName = "1.0"
    }

    signingConfigs {
        create("release") {
            val ks = System.getenv("KEYSTORE_FILE")
            if (ks != null && file(ks).exists()) {
                storeFile = file(ks)
                storePassword = System.getenv("KEYSTORE_PASSWORD")
                keyAlias = System.getenv("KEY_ALIAS")
                keyPassword = System.getenv("KEY_PASSWORD")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("release")
        }
    }

    sourceSets {
        getByName("main") {
            // the collection, the pieces, fonts and the 3D engine, shared with iPhone and the website
            assets.srcDirs("../../Web")
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.16.0")
    implementation("androidx.activity:activity-ktx:1.10.1")
    implementation("androidx.webkit:webkit:1.14.0")
    implementation("com.android.billingclient:billing:8.0.0")
}
