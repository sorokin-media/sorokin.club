/*jslint newcap: true */
/*global inlineAttachment: false */
/**
 * CodeMirror version for inlineAttachment
 *
 * Call inlineAttachment.attach(editor) to attach to a codemirror instance
 */
(function () {
    "use strict";

    var codeMirrorEditor = function (instance) {
        if (!instance.getWrapperElement) {
            throw "Invalid CodeMirror object given";
        }

        this.codeMirror = instance;
    };

    codeMirrorEditor.prototype.getValue = function () {
        return this.codeMirror.getValue();
    };

    codeMirrorEditor.prototype.insertValue = function (val) {
        this.codeMirror.replaceSelection(val);
    };

    codeMirrorEditor.prototype.setValue = function (val) {
        var cursor = this.codeMirror.getCursor();
        this.codeMirror.setValue(val);
        this.codeMirror.setCursor(cursor);
    };

    /**
     * Attach InlineAttachment to CodeMirror
     *
     * @param {CodeMirror} codeMirror
     */
    codeMirrorEditor.attach = function (codeMirror, options) {
        options = options || {};

        var editor = new codeMirrorEditor(codeMirror),
            inlineattach = new inlineAttachment(options, editor),
            el = codeMirror.getWrapperElement();

        el.addEventListener(
            "paste",
            function (e) {
                inlineattach.onPaste(e);
            },
            false
        );

        codeMirror.setOption("onDragEvent", function (data, e) {
            if (e.type === "drop") {
                e.stopPropagation();
                e.preventDefault();

                return inlineattach.onDrop(e);
            }
        });
    };

    var codeMirrorEditor4 = function (instance) {
        codeMirrorEditor.call(this, instance);
    };

    codeMirrorEditor4.attach = function (codeMirror, options) {
        options = options || {};

        var editor = new codeMirrorEditor(codeMirror),
            inlineattach = new inlineAttachment(options, editor),
            el = codeMirror.getWrapperElement();

		    const MEWrapper = el.closest('.comment-markdown-editor-wrapper');

        el.addEventListener(
            "paste",
            function (e) {
                inlineattach.onPaste(e);
            },
            false
        );

        codeMirror.on("drop", function (data, e) {
            if (inlineattach.onDrop(e)) {
                e.stopPropagation();
                e.preventDefault();
                return true;
            } else {
                return false;
            }
        });

        // insert image
        const insertImageBtn = MEWrapper.querySelector('.easyMDE-insert-image-btn');

        if (insertImageBtn) {

          // -- create image input
          const inputImage = document.createElement('input');
          const acceptTypes = options.allowedTypes || '';

          inputImage.type = 'file';
          inputImage.name = 'file-input';
          inputImage.accept = acceptTypes;
          inputImage.style.display = 'none';

          inputImage.addEventListener('change', function(e) {
            inlineattach.onFileInput(e);
            inputImage.value = '';
          })

          MEWrapper.appendChild(inputImage);

          // -- trigger image input
          insertImageBtn.addEventListener('click', function(e) {
            inputImage.click();
          })
        }
    };

    inlineAttachment.editors.codemirror4 = codeMirrorEditor4;
})();
