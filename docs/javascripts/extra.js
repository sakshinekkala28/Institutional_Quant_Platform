/*
===============================================================================
Institutional Quant Platform
MkDocs Material - Custom JavaScript
===============================================================================

This file contains optional enhancements for the documentation site.

Design Goals
------------
- Keep functionality lightweight.
- Avoid modifying MkDocs Material internals.
- Fail gracefully if an element is unavailable.
- Execute only after the DOM is fully loaded.
===============================================================================
*/

(() => {
    "use strict";

    /**
     * Execute once the document is ready.
     */
    document.addEventListener("DOMContentLoaded", () => {
        initializeExternalLinks();
        initializeCodeBlocks();
        initializeTableWrapper();
        initializePrintTimestamp();
    });

    /**
     * Open external links in a new tab.
     */
    function initializeExternalLinks() {
        document.querySelectorAll("a[href]").forEach((link) => {
            const href = link.getAttribute("href");

            if (
                href &&
                /^https?:\/\//i.test(href) &&
                !href.includes(window.location.hostname)
            ) {
                link.setAttribute("target", "_blank");
                link.setAttribute("rel", "noopener noreferrer");
            }
        });
    }

    /**
     * Add a CSS hook to syntax-highlighted code blocks.
     */
    function initializeCodeBlocks() {
        document.querySelectorAll("pre > code").forEach((block) => {
            block.parentElement.classList.add("iqp-code-block");
        });
    }

    /**
     * Wrap wide tables for improved responsiveness.
     */
    function initializeTableWrapper() {
        document.querySelectorAll(".md-typeset table").forEach((table) => {
            if (table.parentElement.classList.contains("iqp-table-wrapper")) {
                return;
            }

            const wrapper = document.createElement("div");
            wrapper.className = "iqp-table-wrapper";
            wrapper.style.overflowX = "auto";

            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        });
    }

    /**
     * Add a generated timestamp when printing documentation.
     */
    function initializePrintTimestamp() {
        window.addEventListener("beforeprint", () => {
            const existing = document.getElementById("iqp-print-timestamp");

            if (existing) {
                existing.remove();
            }

            const stamp = document.createElement("div");
            stamp.id = "iqp-print-timestamp";
            stamp.style.marginTop = "2rem";
            stamp.style.fontSize = "0.8rem";
            stamp.style.color = "#666";

            stamp.textContent =
                "Generated: " + new Date().toLocaleString();

            document.body.appendChild(stamp);
        });
    }
})();