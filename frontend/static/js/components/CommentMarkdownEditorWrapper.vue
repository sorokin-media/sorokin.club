<template>
  <div class="comment-markdown-editor-wrapper" :class="{'comment-markdown-editor-wrapper--separate' : isSeparateFormFooter}">

    <!-- Body -->
    <div
      class="comment-markdown-editor-wrapper__body"
      :class="componentClasses.body"
    >

      <slot></slot>

      <comment-markdown-editor :enableToolbar="enableToolbar" :class="editorSettings.class" :post-slug="editorSettings.postSlug">
        <slot name="form-text"></slot>
      </comment-markdown-editor>

      <slot name="form-errors"></slot>

    </div>

    <!-- Footer / Actions -->
    <div
        v-if="!isSeparateFormFooter"
        class="comment-markdown-editor-wrapper__footer"
        :class="componentClasses.footer"
    >

        <div class="comment-markdown-editor-wrapper__actions">
            <button type="button" class="button easyMDE-insert-image-btn comment-markdown-editor-wrapper__action-item" aria-label="Загрузить изображение" title="Загрузить изображение">
                <svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="605.113px" height="605.113px" viewBox="0 0 605.113 605.113" style="enable-background:new 0 0 605.113 605.113;" xml:space="preserve"> <g> <g> <path d="M529.473,113.459h-56.729l-18.91-37.82C442.695,53.628,436.91,37.82,416.016,37.82H189.097 c-20.895,0-27.797,18.04-37.82,37.819l-18.91,37.82H75.639C33.867,113.459,0,147.326,0,189.098v302.556 c0,41.771,33.867,75.639,75.639,75.639h453.835c41.771,0,75.639-33.867,75.639-75.639V189.098 C605.111,147.327,571.244,113.459,529.473,113.459z M302.556,491.654c-83.543,0-151.278-67.734-151.278-151.277 s67.735-151.278,151.278-151.278c83.543,0,151.278,67.735,151.278,151.278S386.1,491.654,302.556,491.654z"/> <path d="M302.556,226.918c-62.667,0-113.459,50.792-113.459,113.459c0,62.668,50.792,113.459,113.459,113.459 c62.667,0,113.459-50.791,113.459-113.459S365.223,226.918,302.556,226.918z"/> </g> </g> </svg>
            </button>
        </div>

        <div class="comment-markdown-editor-wrapper__footer-content">
            <slot name="form-footer"></slot>
        </div>

    </div>

    <template v-else>
        <div class="comment-markdown-editor-wrapper__actions">
            <button type="button" class="button easyMDE-insert-image-btn comment-markdown-editor-wrapper__action-item" aria-label="Загрузить изображение" title="Загрузить изображение">
                <svg version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="605.113px" height="605.113px" viewBox="0 0 605.113 605.113" style="enable-background:new 0 0 605.113 605.113;" xml:space="preserve"> <g> <g> <path d="M529.473,113.459h-56.729l-18.91-37.82C442.695,53.628,436.91,37.82,416.016,37.82H189.097 c-20.895,0-27.797,18.04-37.82,37.819l-18.91,37.82H75.639C33.867,113.459,0,147.326,0,189.098v302.556 c0,41.771,33.867,75.639,75.639,75.639h453.835c41.771,0,75.639-33.867,75.639-75.639V189.098 C605.111,147.327,571.244,113.459,529.473,113.459z M302.556,491.654c-83.543,0-151.278-67.734-151.278-151.277 s67.735-151.278,151.278-151.278c83.543,0,151.278,67.735,151.278,151.278S386.1,491.654,302.556,491.654z"/> <path d="M302.556,226.918c-62.667,0-113.459,50.792-113.459,113.459c0,62.668,50.792,113.459,113.459,113.459 c62.667,0,113.459-50.791,113.459-113.459S365.223,226.918,302.556,226.918z"/> </g> </g> </svg>
            </button>
        </div>

        <div class="comment-markdown-editor-wrapper__footer-content">
            <slot name="form-footer"></slot>
        </div>
    </template>

  </div>

</template>

<script>
import CommentMarkdownEditor from "../components/CommentMarkdownEditor.vue";

export default {
  components: {
    CommentMarkdownEditor,
  },

  props: {
    isSeparateFormFooter: {
        type: Boolean,
        default: false,
    },

    enableToolbar: {
        type: Boolean,
        default: false,
    },

    componentClasses: {
      type: Object,
      default: () => {
        return {
          body: 'comment-form-body',
          footer: 'comment-form-button',
        }
      }
    },

    editorSettings: {
      type: Object,
      default: () => {
        return {
          class: '',
          postSlug: '',
        }
      }
    }
  },

  data() {
    return {

    }
  },
}
</script>
