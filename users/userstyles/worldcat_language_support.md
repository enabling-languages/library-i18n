# Worldcat language support


## CSS overrides

### Stylish (Firefox)

```css
@-moz-document domain("www.worldcat.org") {
    .vernacular {
        direction: auto;
        color: darkslategray ;
    }
    .vernacular:lang(ar) {
        direction: rtl;
        font-family: "Scheherazade New", Amiri;
    }
}
```

### Custom Style Script (MS Edge Extension)

```css
.vernacular {
    direction: auto;
    color: darkslategray ;
}
.vernacular:lang(ar) {
    direction: rtl;
    font-family: "Scheherazade New", Amiri;
}
```

## Tests

* [Arabic](https://www.worldcat.org/oclc/929494926)
* Russian:
    [1](https://www.worldcat.org/oclc/891462395)



ᠲᠡᠦᠬᠡ
түүх
http://trans.mglip.com/EnglishC2T.aspx

ᠮᠠᠨ ᠤ ᠤᠯᠤᠰ ᠤᠨ ᠡᠷᠲᠡᠨ ᠤ ᠦᠶ ᠡ ᠢᠢᠨ ᠪᠠᠭᠤᠷᠠᠢ ᠪᠡᠷ ᠬᠦᠴᠦᠷᠬᠡᠭ ᠢ ᠢᠯᠠᠭᠰᠠᠨ ᠲᠡᠶᠢᠨ ᠦ ᠵᠢᠱᠢᠶ ᠡ



```js
(function() {
    'use strict';
    console.log("hello, world!");
})();
```

---

## GreaseMonkey

```js
// ==UserScript==
// @name     Worldcat Language Support
// @version  1
// @include  https://www.worldcat.org/*
// @grant    GM_addStyle
// @require  https://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==

$(document).ready(function() {
  $( ".vernacular" ).attr( 'dir', 'auto' ).css( "font-family", "Charis SIL" ).css( "color", "darkslategray" );
  $( "span.vernacular" ).parent().attr( 'dir', 'auto' ).css( "font-family", "Charis SIL" ).css( "color", "darkslategray" );
  $( "div.vernacular" ).parent( "strong" ).attr( 'dir', 'auto' ).css( "font-family", "Charis SIL" ).css( "color", "darkslategray" );
  $( "div.vernacular" ).parent( "h1.title" ).attr( 'dir', 'auto' ).css( "font-family", "Charis SIL" ).css( "color", "darkslategray" );
  
  // Arabic rules
  $( ".vernacular:lang(ar)" ).attr('dir', 'rtl').css( "font-family", "Scheherazade New, Amiri" ).css( "color", "darkslategray" );
  $( "span.vernacular:lang(ar)" ).parent().attr( 'dir', 'rtl' ).css( "font-family", "Scheherazade New, Amiri" ).css( "color", "darkslategray" );
  $( "div.vernacular:lang(ar)" ).parent( "strong" ).attr( 'dir', 'rtl' ).css( "font-family", "Scheherazade New, Amiri" ).css( "color", "darkslategray" );
  $( "div.vernacular:lang(ar)" ).parent( "h1.title" ).attr( 'dir', 'rtl' ).css( "font-family", "Scheherazade New, Amiri" ).css( "color", "darkslategray" );
});
```


---

Migrate to vanilla JS:

* [Cheat sheet for moving from jQuery to vanilla JavaScript](https://tobiasahlin.com/blog/move-from-jquery-to-vanilla-javascript/)



---

Tampermonkey template:

```js
// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://wiki.greasespot.net/@grant
// @icon         https://www.google.com/s2/favicons?domain=greasespot.net
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Your code here...
})();
```

---

Search terms:

អក្សរសិល្ប៍ - literature (km)
ວັນນະຄະດີ - literature (lo)
ادبیات - literature (fa)
история - history (ru)
lịch sử - history (vi)
