# Adding a piece to Star Song later

New pieces join the paid collection automatically. Anyone who has bought `starsong.bundle` gets them free with the next update, so there's nothing new to set up in either store.

The easiest way is to ask me ("add <artifact name> to Star Song"), and I'll prepare the piece the same way as the others: offline fonts, one look, endless play, the Collection button and a thumbnail. If you do it yourself:

1. **Make a folder** `Web/pieces/<id>/` containing the piece's `index.html` and a square `thumb.jpg` (about 720 × 720).
2. **In the piece's `<head>`, before its own scripts, add:**
   ```html
   <link rel="stylesheet" href="../../fonts/fonts.css">
   <script src="../../pieces.js"></script>
   <script src="../../shared/host.js"></script>
   ```
   Any font it uses must be in `Web/fonts/` (listed in `fonts.css`), and nothing may load from the internet. The apps work offline.
3. **Choose where the Collection button sits** with `<html lang="en" data-home="tl">`: `tl`, `tc` or `tr` for top left, centre or right; `bl` or `br` for the bottom corners.
4. **Add it to `Web/pieces.js`:**
   ```js
   { id: 'my-piece', title: 'My Piece', blurb: 'One sentence about it.' },
   ```
   Leave out `free: true`, so it's part of the paid collection.
5. **Publish:** the website updates by itself. Then run the iPhone and Android workflows, submit the new builds as an update (version 1.1 and so on), and add new screenshots if you like.
