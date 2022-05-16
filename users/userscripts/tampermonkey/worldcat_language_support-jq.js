// ==UserScript==
// @name     Worldcat Language Support (jQuery)
// @version  1
// @include  https://www.worldcat.org/*
// @grant    none
// @require  https://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==

$(document).ready(function() {
    $( "#bibdata").css( "font-family", "Charis SIL" );
    $( "#details").css( "font-family", "Charis SIL" );
    $( ".vernacular" ).attr( 'dir', 'auto' );

    // Arabic rules
    $( ".vernacular:lang(ar)" ).attr('dir', 'rtl').css( "font-family", "Scheherazade New, Amiri" );
});
