<template>
    <a :href="telegramLink" @click="telegramClick" class="tg-btn" type="button">
        <span>Получать в  Telegram</span>
        <div class="icon">
            <img src="/static/images/icons/telegram-black-stroke.png" alt="">
        </div>
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
