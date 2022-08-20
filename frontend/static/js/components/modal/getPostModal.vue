<template>
  <vue-modal v-if="isModal && isActive" class="post-modal" @close="closeModal">
    <div class="post-modal__header">
      <p class="post-modal__title">
      <span>Делимся самым</span> <span><b>интересным</b></span>
      </p>
    </div>

    <div class="post-modal__body">
      <div class="post-modal__content">
        <div class="post-modal__content-text">
            <p class="bold"><b>Лучшая статья</b></p>
            <p>из <b>закрытой</b> части клуба</p>
            <p class="bold"><b>Раз в неделю</b></p>
        </div>

        <div class="post-modal__content-logo">
            <img src="/static/images/logo/sorokin-club.png" alt="">
        </div>
      </div>

      <div class="post-modal__actions">
        <div class="post-modal__action-row">
            <a :href="telegramLink" @click="telegramClick" class="post-modal__btn post-modal__btn--blue" type="button">
                <span>Получать в  Telegram</span>
                <div class="icon">
                    <svg width="43" height="39" viewBox="0 0 43 39" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M37.0247 6.0402L5.25849 17.1503C3.09057 17.9401 3.10311 19.0369 4.86074 19.5261L13.0164 21.8336L31.8862 11.0354C32.7785 10.5431 33.5937 10.8079 32.9236 11.3474L17.6353 23.8616H17.6317L17.6353 23.8632L17.0727 31.4877C17.8969 31.4877 18.2606 31.1448 18.7229 30.7402L22.6842 27.2464L30.9241 32.7666C32.4434 33.5254 33.5346 33.1354 33.9126 31.4909L39.3217 8.37045C39.8753 6.35707 38.4742 5.44545 37.0247 6.0402V6.0402Z" fill="#FAFAFA"/>
                    </svg>
                </div>
            </a>
        </div>
      </div>
    </div>

    <div class="post-modal__footer">
      <p class="post-modal__under-text">Присылаем полные версии статей. Бесплатно и без регистрации.</p>
    </div>
  </vue-modal>

  <div v-else-if="!isModal" class="post-modal-section">
    <div class="post-modal-section__container">
      <div class="post-modal">
        <div class="post-modal__container">
          <div class="post-modal__header">
            <p class="post-modal__title">
            <span>Делимся самым</span> <span><b>интересным</b></span>
            </p>
          </div>

          <div class="post-modal__body">
            <div class="post-modal__content">
              <div class="post-modal__content-text">
                  <p class="bold"><b>Лучшая статья</b></p>
                  <p>из <b>закрытой</b> части клуба</p>
                  <p class="bold"><b>Раз в неделю</b></p>
              </div>

              <div class="post-modal__content-logo">
                  <img src="/static/images/logo/sorokin-club.png" alt="">
              </div>
            </div>

            <div class="post-modal__actions">
              <div class="post-modal__action-row">
                  <a :href="telegramLink" @click="telegramClick" class="post-modal__btn post-modal__btn--blue" type="button">
                      <span>Получать в  Telegram</span>
                      <div class="icon">
                          <svg width="43" height="39" viewBox="0 0 43 39" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M37.0247 6.0402L5.25849 17.1503C3.09057 17.9401 3.10311 19.0369 4.86074 19.5261L13.0164 21.8336L31.8862 11.0354C32.7785 10.5431 33.5937 10.8079 32.9236 11.3474L17.6353 23.8616H17.6317L17.6353 23.8632L17.0727 31.4877C17.8969 31.4877 18.2606 31.1448 18.7229 30.7402L22.6842 27.2464L30.9241 32.7666C32.4434 33.5254 33.5346 33.1354 33.9126 31.4909L39.3217 8.37045C39.8753 6.35707 38.4742 5.44545 37.0247 6.0402V6.0402Z" fill="#FAFAFA"/>
                          </svg>
                      </div>
                  </a>
              </div>
            </div>
          </div>

          <div class="post-modal__footer">
            <p class="post-modal__under-text">Присылаем полные версии статей. Бесплатно и без регистрации.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import VueYandexMetrika from 'vue-yandex-metrika'
import vueModal from "./vueModal.vue";
import { getCookie, isMobile } from "../../common/utils"

Vue.use(VueYandexMetrika, {
    id: 88682790,
    env: process.env.NODE_ENV,
    options: {
        clickmap:true,
        trackLinks:true,
        accurateTrackBounce:true
    }
})

export default {
  name: 'get-post-modal',
  components: {
    vueModal,
  },

  props: {
    isModal: {
      default: true,
    }
  },

  data () {
    return {
        delayOpen: 1,
        isActive: false,
        telegramLink: 'tg://resolve?domain=sorokinclub_public_bot&start=STARTWORD',
    }
  },

  mounted () {

    this.generateTelegramLink();

    if (this.isModal) {
         setTimeout(() => {
            this.isActive = true;
            this.$metrika.reachGoal('popup_view');
        }, this.delayOpen * 1000)
    } else {
        this.$metrika.reachGoal('popup_view');
    }

  },

  methods: {
    closeModal () {
        this.isActive = false;
    },

    generateTelegramLink () {
      const url = new URL(window.location);
      const search_referrer = getCookie('search_referrer') || '';
      let startWord = getCookie('utm_source') ? getCookie('utm_source') : search_referrer + url.pathname.replace(/[\/\\]+/gm, '_');

      this.telegramLink = `tg://resolve?domain=sorokinclub_public_bot&start=${ startWord }`;
    },

    telegramClick () {
        this.$metrika.reachGoal('popup_tg_click');
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
