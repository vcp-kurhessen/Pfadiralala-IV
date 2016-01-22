/*
* Description: An Adobe Illustrator script that export each layer as a separate PDF file. For Illustrator CS 4+.
* Usage: Layer name will be appended to the file name. Rename layers if necessary.
* This is an early version that has not been sufficiently tested. Use at your own risks.
* License: GNU General Public License Version 3. (http://www.gnu.org/licenses/gpl-3.0-standalone.html)
*
* Copyright (c) 2010, William Ngan
* http://www.metaphorical.net

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/


var doc = app.activeDocument;
var docname = (doc.name.split('.'))[0]; // name
var doc_artboard = doc.artboards[0].artboardRect;

if (app.documents.length > 1) {
		alert( "Please close other documents, and run the script again");
} else {

	var ok = confirm( "Please save your original file before continue.\n\nLayer files will be saved in the same folder as the original file. Original file will be closed without saving.\n\nContinue?" );

	if (ok) {
		
		// prepare layers
		for(var i=0; i<doc.layers.length; i++) {
			doc.layers[i].visible = false;
		}


		// go through each layers
		for(var i=0; i<doc.layers.length; i++) {
			app.activeDocument = doc;


			if (i>0) doc.layers[i-1].visible = false;
			doc.layers[i].visible = true;
			doc.activeLayer = doc.layers[i];

			saveAI( doc.path, doc.activeLayer.name, i );
		}


		// close original file without saving
		doc.close( SaveOptions.DONOTSAVECHANGES );
	
	}

}


function saveAI( path, name, id ) {
	
	var currlayer = doc.layers[id];	
	var g = currlayer.groupItems.add();
	group( g, currlayer.pageItems );	
	
	var t = g.top;
	var l = g.left;


	var newdoc = app.documents.add ( doc.documentColorSpace, doc.width, doc.height);
	newdoc.artboards[0].artboardRect = doc_artboard;
	var newlayer = newdoc.layers[0];
	
	g.duplicate( newlayer, ElementPlacement.PLACEATBEGINNING );
	newlayer.pageItems[0].top = t;
	newlayer.pageItems[0].left = l;

	path.changePath( docname+"_"+name+".pdf" );

	var saveOpts = new PDFSaveOptions();
	saveOpts.compatibility = PDFCompatibility.ACROBAT6;
	saveOpts.generateThumbnails = true;
	saveOpts.preserveEditability = true;
				
	newdoc.saveAs( path, saveOpts );
	newdoc.close( SaveOptions.DONOTSAVECHANGES );
	
				
	// wait for the new file to save and close before continue.
	// A callback function (if possible) will be better than a while loop for sure.
	while (app.documents.length > 1) {
		continue;
	}
}


function group( gg, items ) {

	var newItem;
	for(var i=items.length-1; i>=0; i--) {

		
		if (items[i]!=gg) { 
			newItem = items[i].move (gg, ElementPlacement.PLACEATBEGINNING);
		}
	}
	return newItem;
}
