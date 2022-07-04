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

        // Set cursor by textarea (if textarea displays)
        const textArea = this.codeMirror.getTextArea();
        const curCursorPos = this.codeMirror.getCursor();
        const textAreaLineArr = textArea.value.substr(0, textArea.selectionStart).split("\n");

        let cursorPosition = {
            line: textAreaLineArr.length - 1,
            ch: textAreaLineArr[textAreaLineArr.length - 1].length,
        }

        if (curCursorPos.ch != 0 || curCursorPos.line != 0) {
            cursorPosition = this.codeMirror.getCursor();
        }

        this.codeMirror.setCursor(cursorPosition, 1);

        // Do replace
        this.codeMirror.replaceSelection(val);
    };

    codeMirrorEditor.prototype.setValue = function (val) {
        var cursor = this.codeMirror.getCursor();
        this.codeMirror.setValue(val);
        this.codeMirror.setCursor(cursor);
    };

    codeMirrorEditor.prototype.setSelection = function (e) {

        const textArea = this.codeMirror.getTextArea();
        const selectionFromStart = textArea.value.substr(0, textArea.selectionEnd).split("\n")
        const selectionArr = textArea.value.substr(textArea.selectionStart, textArea.selectionEnd - textArea.selectionStart).split("\n");

        const selectionStart = {}
        const selectionEnd = {}

        selectionStart.line = selectionFromStart.length - selectionArr.length;
        selectionStart.ch = selectionFromStart[selectionStart.line].length - selectionArr[0].length;

        selectionEnd.line = selectionFromStart.length - 1;
        selectionEnd.ch = selectionFromStart[selectionStart.line + selectionArr.length - 1].length;

        this.codeMirror.setSelection(selectionStart, selectionEnd);
    };

    codeMirrorEditor.prototype.syncCursorPosition = function (e) {

        const curCursorPos = this.codeMirror.getCursor();
        const textArea = this.codeMirror.getTextArea();
        const textAreaLineArr = textArea.value.substr(0, textArea.selectionStart).split("\n");

        let cursorPosition = {
            line: textAreaLineArr.length - 1,
            ch: textAreaLineArr[textAreaLineArr.length - 1].length,
        }

        if (curCursorPos.ch != 0 || curCursorPos.line != 0) {
            cursorPosition = this.codeMirror.getCursor();
        }

        this.codeMirror.setCursor(cursorPosition, 1);
    };

    codeMirrorEditor.prototype.textAreaFocusCursor = function (e) {

        const curCursorPos = this.codeMirror.getCursor();
        const textArea = this.codeMirror.getTextArea();
        const textAreaLineArr = textArea.value.substr(0, textArea.selectionStart).split("\n");

        let selectionStart = 0;

        for (let i = 0; i < textAreaLineArr.length; i++) {
            const line = textAreaLineArr[i];

            if (i > curCursorPos.line) {
                break;
            }

            if (i == curCursorPos.line) {
                selectionStart += curCursorPos.ch;
            } else {
                selectionStart += line.length + 1;
            }
        }

        textArea.selectionStart = selectionStart;
        textArea.selectionEnd = selectionStart;

        textArea.focus();

        setTimeout(() => {
            textArea.focus();
        }, 100);
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
            el = codeMirror.getWrapperElement(),
            markdownEditor = el.closest('.comment-markdown-editor') || el;

        // Text area connect actions
        if (markdownEditor && markdownEditor.classList.contains('comment-markdown-editor--mobile')) {
            const textarea  = markdownEditor.querySelector('.markdown-editor-invisible') || markdownEditor.querySelector('.markdown-editor-full') || markdownEditor;

            // Paste event
            textarea.addEventListener(
                "paste",
                function (e) {
                    inlineattach.onPaste(e);
                },
                false
            );

            // Sync cursor
            textarea.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                inlineattach.syncCursorPosition(e);
            });

            textarea.addEventListener('input', function(e) {
                e.stopPropagation();

                inlineattach.syncCursorPosition(e);
            });

            // Select event
            textarea.addEventListener('select', function(e) {
                const el = e.target;
                const sel = el.value.substr(el.selectionStart, el.selectionEnd);

                inlineattach.onSelection(e);
            });

            // Focus textarea
            textarea.addEventListener('focus', function(e) {
                e.preventDefault();
                e.stopPropagation();
            });

            // Focus codemirror
            codeMirror.on('focus', function(e) {
                inlineattach.textAreaFocusCursor();
            });
        }

        // Paste Event
        el.addEventListener(
            "paste",
            function (e) {
                inlineattach.onPaste(e);
            },
            false
        );

        // Drop Event
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
        const MEWrapper = el.closest('.comment-markdown-editor-wrapper') || el.closest('.comment-markdown-editor') || el;
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
