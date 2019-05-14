var addSorting = (function () {
    "use strict";

    var cols,
        currentSort = {
            index: 3,
            desc: true
        };

    // returns the summary table element
    function getTable() { return document.querySelector('.sortable'); }
    // returns the thead element of the summary table
    function getTableHeader() { return getTable().querySelector('thead tr'); }
    // returns the tbody element of the summary table
    function getTableBody() { return getTable().querySelector('tbody'); }
    // returns the th element for nth column
    function getNthColumn(n) { return getTableHeader().querySelectorAll('th')[n]; }

    // loads all columns
    function loadColumns() {		
        var colNodes = getTableHeader().querySelectorAll('th'),
            colNode,
            cols = [],
            col,
            i;

        for (i = 0; i < colNodes.length; i += 1) {
            colNode = colNodes[i];
            col = {
                key: colNode.getAttribute('data-col'),
                sortable: !colNode.getAttribute('data-nosort'),
                type: colNode.getAttribute('data-type') || 'string'
            };
            cols.push(col);
            if (col.sortable) {
                col.defaultDescSort = true; // col.type === 'number';
                colNode.innerHTML = colNode.innerHTML + '<span class="sorter"></span>';
            }
        }
        return cols;
    }
    // attaches a data attribute to every tr element with an object
    // of data values keyed by column name
    function loadRowData(tableRow) {
        var tableCols = tableRow.querySelectorAll('td'),
            colNode,
            col,
            data = {},
            i,
            val;
        for (i = 0; i < tableCols.length; i += 1) {
            colNode = tableCols[i];
            col = cols[i];
            val = colNode.getAttribute('data-value');
            if (col.type === 'number') {
                val = Number(val);
            }
            data[col.key] = val;
        }
        return data;
    }
    // loads all row data
    function loadData() {
        var rows = getTableBody().querySelectorAll('tr'),
            i;

        for (i = 0; i < rows.length; i += 1) {
            rows[i].data = loadRowData(rows[i]);
        }

		// if (typeof iserr !== 'undefined'){
		// 	if (getCookie('indexer')) {
		// 		currentSort.index = getCookie('indexer');
		// 		currentSort.desc = (getCookie('descer')=="true")?true:false;
		// 		}
		// 	sortByIndex(1, true)
		// 	sortByIndex(2, true)
		// 	sortByIndex(3, true)
		// }
		// else {
		// 	if (getCookie('index')) {
		// 		currentSort.index = getCookie('index');
		// 		currentSort.desc = (getCookie('desc')=="true")?true:false;
		// 	}
		// 	sortByIndex(currentSort.index, currentSort.desc)
		// }
    }
    // sorts the table using the data for the ith column
    function sortByIndex(index, desc) {
		if (typeof iserr !== 'undefined'){
			setCookie('indexer', index);
			setCookie('descer', desc);
		}   
		else {
			setCookie('index', index);
			setCookie('desc', desc);
		}

		
        var key = cols[index].key,
            sorter = function (a, b) {
                a = a.data[key];
                b = b.data[key];
                return a < b ? -1 : a > b ? 1 : 0;
            },
            finalSorter = sorter,
            tableBody = document.querySelector('.sortable  tbody'),
            rowNodes = tableBody.querySelectorAll('tr'),
            rows = [],
            i;

        if (desc) {
            finalSorter = function (a, b) {
                return -1 * sorter(a, b);
            };
        }

        for (i = 0; i < rowNodes.length; i += 1) {
            rows.push(rowNodes[i]);
            tableBody.removeChild(rowNodes[i]);
        }

        rows.sort(finalSorter);

        for (i = 0; i < rows.length; i += 1) {
            tableBody.appendChild(rows[i]);
        }
		
    }
    // removes sort indicators for current column being sorted
    function removeSortIndicators() {
        var col = getNthColumn(currentSort.index),
            cls = col.className;

        cls = cls.replace(/ sorted$/, '').replace(/ sorted-desc$/, '');
        col.className = cls;
    }
    // adds sort indicators for current column being sorted
    function addSortIndicators() {
        getNthColumn(currentSort.index).className += currentSort.desc ? ' sorted-desc' : ' sorted';
    }
    // adds event listeners for all sorter widgets
    function enableUI() {
        var i,
            el,
            ithSorter = function ithSorter(i) {
                var col = cols[i];

                return function () {
                    var desc = col.defaultDescSort;

                    if (currentSort.index === i) {
                        desc = !currentSort.desc;
                    }
                    sortByIndex(i, desc);
                    removeSortIndicators();
                    currentSort.index = i;
                    currentSort.desc = desc;
                    addSortIndicators();
                };
            };
        for (i = 0 ; i < cols.length; i += 1) {
            if (cols[i].sortable) {
                // add the click event handler on the th so users
                // dont have to click on those tiny arrows
                el = getNthColumn(i).querySelector('.sorter').parentElement;
                if (el.addEventListener) {
                    el.addEventListener('click', ithSorter(i));
                } else {
                    el.attachEvent('onclick', ithSorter(i));
                }
            }
        }
    }
    // adds sorting functionality to the UI
    return function () {
        if (!getTable()) {
            return;
        }
        cols = loadColumns();
        loadData(cols);
        addSortIndicators();
        enableUI();
    };
	
//---------- работа с cookie //

	function setCookie(name, value, expires, path, domain, secure) {
		var is_chrome = ((navigator.userAgent.toLowerCase().indexOf('chrome') > -1) &&(navigator.vendor.toLowerCase().indexOf("google") > -1));
		// var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);
		if (is_chrome){
			localStorage.setItem(name, value);}
		else{
			document.cookie= name + "=" + escape(value) +
				((expires) ? "; expires=" + expires.toGMTString() : "") +
				((path) ? "; path=" + path : "") +
				((domain) ? "; domain=" + domain : "") +
				((secure) ? "; secure" : "");
		}
	}

	function getCookie(name) {
		var is_chrome = ((navigator.userAgent.toLowerCase().indexOf('chrome') > -1) &&(navigator.vendor.toLowerCase().indexOf("google") > -1));
		// var isChrome = !!window.chrome && (!!window.chrome.webstore || !!window.chrome.runtime);
		if (is_chrome){
			return localStorage.getItem(name)
		}
		else{
			var dc = document.cookie;
			var prefix = name + "=";
			var begin = dc.indexOf("; " + prefix);
			if (begin == -1) {
				begin = dc.indexOf(prefix);
				if (begin != 0) return null;
			} else {
				begin += 2;
			}
			var end = document.cookie.indexOf(";", begin);
			if (end == -1) {
				end = dc.length;
			}
			return unescape(dc.substring(begin + prefix.length, end));
		}
		return currentSort
	}
	function deleteCookie(name, path, domain) {
		if (getCookie(name)) {
			document.cookie = name + "=" +
				((path) ? "; path=" + path : "") +
				((domain) ? "; domain=" + domain : "") +
				"; expires=Thu, 01-Jan-70 00:00:01 GMT";
		}
	}
//----------//
	
})();

window.addEventListener('load', addSorting);
