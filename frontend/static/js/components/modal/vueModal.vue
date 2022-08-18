<template>
  <transition name="modal">
    <div class="modal__mask" @click="$emit('close')">
      <div class="modal__wrapper">
        <div class="modal__container" @click.stop="">

          <button class="modal__close-btn" aria-label="Закрыть" title="Закрыть" @click="$emit('close')">
            Закрыть
          </button>

          <div class="modal__content">
            <slot></slot>
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

<style lang="scss" scoped>
</style>
