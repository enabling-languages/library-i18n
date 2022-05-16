// ==UserScript==
// @name         Worldcat Language Support
// @namespace    https://enabling-languages.github.io/
// @version      0.2
// @description  Improve non-English text display in WorldCat
// @author       Enabling Languages
// @match        https://www.worldcat.org/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    let elems = [document.getElementById('bibdata'), document.getElementById('details')]
    elems.forEach(elem => {elem.style.fontFamily = "Gentium Plus"})
    document.querySelectorAll(".vernacular").forEach(vern => { vern.setAttribute("dir", "auto")})
    /*
     * Language and script specific rules
     *
     */

    /* Arabic */
    document.querySelectorAll(".vernacular:lang(ar)").forEach(vern => {vern.setAttribute("dir", "rtl"); vern.style.fontFamily = "Scheherazade New, Amiri";})
    /* Persian */
    document.querySelectorAll(".vernacular:lang(fa)").forEach(vern => {vern.setAttribute("dir", "rtl"); vern.style.fontFamily = "Scheherazade New, Amiri";})
})();


