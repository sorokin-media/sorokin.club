<template>
  <transition name="modal">
    <div class="modal-mask" @click="$emit('close')">
      <div class="modal-wrapper">
        <div class="modal-container" @click.stop="">

          <button class="modal-close-button" aria-label="Закрыть" title="Закрыть" @click="$emit('close')">
            Закрыть
          </button>

          <div class="modal-container__content">

            <div class="modal-header">

              <slot name="header">
                default header
              </slot>

            </div>

            <div class="modal-body">

              <slot name="body">
                default body
              </slot>

            </div>

            <div class="modal-footer">

              <slot name="footer">
                default footer
              </slot>

            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'vue-modal',
}
</script>

<style scoped>

    .modal-mask {
        position: fixed;
        z-index: 9998;
        top: 0;
        left: 0;

        width: 100%;
        height: 100%;

        display: table;

        background-color: rgba(0, 0, 0, 0.5);
        transition: opacity 0.3s ease;
    }

    .modal-wrapper {
        display: table-cell;
        vertical-align: middle;

        padding: 0 20px;
    }

    .modal-container {
      position: relative;

      width: 100%;
      max-width: 800px;

      max-height: calc(100vh - 40px);

      overflow: auto;

      margin: 0px auto;
    }

    .modal-container__content {
        margin-right: 35px;
        padding: 3rem;
        padding-top: 4rem;

        background-color: #fafafa;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);

        transition: all 0.3s ease;
    }

    .modal-body {
        margin-top: 4rem;
        margin-bottom: 2.5rem;
    }

    .modal-close-button {
        position: relative;

        cursor: pointer;

        margin-right: 0;
        margin-bottom: -10px;
        margin-left: auto;

        display: block;

        width: 40px;
        height: 40px;

        font-size: 0;
        color: transparent;

        background-color: transparent;
        border:0;
    }

    .modal-close-button::before,
    .modal-close-button::after {
        content: '';

        position: absolute;
        left: 50%;
        top: 50%;

        display: block;

        width: 75%;
        height: 4px;

        background-color: #fafafa;
        border-radius: 20px;
    }

    .modal-close-button::before {
        transform: translate(-50%, -50%) rotate(45deg);
    }

    .modal-close-button::after {
        transform: translate(-50%, -50%) rotate(-45deg);
    }

    .modal-close-button:hover,
    .modal-close-button:focus {
        opacity: 0.7;
    }

    .modal-header {
        padding-bottom: 0;
        border-bottom: 0;
    }

    .modal-footer {
        padding-top: 0;
        border-top: 0;
    }

    .modal-enter {
        opacity: 0;
    }

    .modal-leave-active {
        opacity: 0;
    }

    .modal-enter .modal-container,
    .modal-leave-active .modal-container {
        -webkit-transform: scale(1.1);
        transform: scale(1.1);
    }

    .modal-header h3 {
        margin-top: 0;
        color: #333;
    }

  @media (max-width: 768px) {
    .modal-close-button {
      position: absolute;
      right: 0;
      top: 0;
    }

    .modal-close-button::before,
    .modal-close-button::after {
      background-color: #282C35;
    }

    .modal-container__content {
      padding: 1.5rem;
      padding-top: 3rem;

      margin-right: 0;
    }

    .modal-body {
      margin-top: 3rem;
      margin-bottom: 2rem;
    }
  }

</style>
