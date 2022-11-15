<template>
    <div v-if="!isCustom" class="telegram__button" :class="classes">
        <a :href="telegramLink" @click="telegramClick" class="btn-tg" target="_blank">
            <span>получать в telegram</span>
            <svg width="57" height="47" viewBox="0 0 57 47" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4.034 20.45S28.802 10.285 37.391 6.706C40.684 5.274 51.851.693 51.851.693s5.154-2.004 4.725 2.863c-.143 2.005-1.289 9.02-2.434 16.608-1.718 10.737-3.58 22.477-3.58 22.477s-.286 3.293-2.72 3.865c-2.433.573-6.441-2.004-7.157-2.577-.573-.429-10.738-6.872-14.46-10.021-1.002-.86-2.148-2.577.143-4.581 5.154-4.725 11.31-10.595 15.032-14.317 1.718-1.718 3.436-5.726-3.722-.859-10.165 7.015-20.186 13.6-20.186 13.6s-2.29 1.432-6.586.144C6.611 26.607 1.6 24.888 1.6 24.888s-3.435-2.148 2.434-4.438Z"/></svg>
        </a>
        <div class="telegram__button-sub">Делимся самым интересным</div>
    </div>
    <a
      v-else

      :href="telegramLink"
      :class="classes"
      @click="telegramClick"

      class="btn-tg"
      target="_blank"
    >
      <slot></slot>
    </a>
</template>

<script>
import Vue from 'vue';
import VueYandexMetrika from 'vue-yandex-metrika';
import { getCookie } from "../../common/utils";

Vue.use(VueYandexMetrika, {
    id: 88682790,
    env: process.env.NODE_ENV,
    options: {
        clickmap:true,
        trackLinks:true,
        accurateTrackBounce:true
    }
});

export default {
  name: 'tg-button',

  props: {
    isCustom: {
      type: Boolean,
      default: false,
    },

    classes: {
      type: Array,
      default: () => [],
    }
  },

  data () {
    return {
        telegramLink: 'tg://resolve?domain=sorokinclub_public_bot&start=STARTWORD',
    }
  },

  mounted () {
    this.generateTelegramLink();
    this.$metrika.reachGoal('popup_view');
  },

  methods: {
    generateTelegramLink () {
      const url = new URL(window.location);
      const search_referrer = getCookie('search_referrer') || '';
      let startWord = getCookie('utm_source') ? getCookie('utm_source') : search_referrer + url.pathname.replace(/[\/\\]+/gm, '_');

      this.telegramLink = `tg://resolve?domain=sorokinclub_public_bot&start=${ startWord }`;
    },

    telegramClick () {
        this.$metrika.reachGoal('tg_miniland');
    }
  }
}
</script>

<style scoped>
</style>
