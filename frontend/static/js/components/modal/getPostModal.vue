<template>
  <vue-modal v-if="isActive" @close="closeModal">
    <template v-slot:header>
      <p class="title">
       <span>Делимся самым</span> <span><b>интересным</b></span>
    </p>
    </template>

    <template v-slot:body>
      <div class="content">
        <div class="content-text">
            <p class="content-text-bold"><b>Лучшая статья</b></p>
            <p>из <b>закрытой</b> части клуба</p>
            <p class="content-text-bold"><b>Раз в неделю</b></p>
        </div>

        <div class="content-logo">
            <img src="/static/images/logo/sorokin-club.png" alt="">
        </div>
      </div>

      <div class="actions">
        <div class="action__row">
            <a :href="telegramLink" @click="telegramClick" class="btn btn--blue" type="button">
                <span>Получать в  Telegram</span>
                <div class="icon">
                    <svg width="43" height="39" viewBox="0 0 43 39" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M37.0247 6.0402L5.25849 17.1503C3.09057 17.9401 3.10311 19.0369 4.86074 19.5261L13.0164 21.8336L31.8862 11.0354C32.7785 10.5431 33.5937 10.8079 32.9236 11.3474L17.6353 23.8616H17.6317L17.6353 23.8632L17.0727 31.4877C17.8969 31.4877 18.2606 31.1448 18.7229 30.7402L22.6842 27.2464L30.9241 32.7666C32.4434 33.5254 33.5346 33.1354 33.9126 31.4909L39.3217 8.37045C39.8753 6.35707 38.4742 5.44545 37.0247 6.0402V6.0402Z" fill="#FAFAFA"/>
                    </svg>
                </div>
            </a>
        </div>
      </div>
    </template>

    <template v-slot:footer>
      <p class="under-text">Присылаем полные версии статей. Бесплатно и без регистрации.</p>
    </template>
  </vue-modal>
</template>

<script>
import Vue from 'vue'
import VueYandexMetrika from 'vue-yandex-metrika'
import vueModal from "./vueModal.vue";
import { getCookie } from "../../common/utils"

Vue.use(VueYandexMetrika, {
    id: 88682790,
    // env: 'production',
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

  data () {
    return {
        delayOpen: 30,
        isActive: false,
        telegramLink: 'tg://resolve?domain=sorokinclub_public_bot&start=STARTWORD',
    }
  },

  mounted () {
    this.generateTelegramLink();

    setTimeout(() => {
        this.isActive = true;
        this.$metrika.reachGoal('popup_view');
    }, this.delayOpen * 1000)
  },

  methods: {
    closeModal () {
        this.isActive = false;
    },

    generateTelegramLink () {
      const url = new URL(window.location);
      const targetKeyName = 'utm_source';
      const startWord = getCookie(targetKeyName) ? getCookie(targetKeyName) : url.pathname.replace(/[\/\\]+/gm, '_');

      this.telegramLink = `tg://resolve?domain=sorokinclub_public_bot&start=${ startWord }`;
    },

    telegramClick () {
        this.$metrika.reachGoal('popup_tg_click');
    }
  }
}
</script>

<style scoped>
.title {
    font-size: 2.7rem;
    margin: 0;

    display: flex;
    flex-direction: column;
    text-align: center;
    align-items: center;

    line-height: 1;

    font-weight: bold;
    color: #282C35;
}

.title b {
    display: block;
    padding: 0.8rem 2.1rem;

    color: #fafafa;
    background-color: #282C35;
    border-radius: 7px;
}

.title span {
    display: block;

    margin-bottom: 1.5rem;
}

.title span:last-child {
    margin-bottom: 0;
}

.content {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;

    text-align: center;

    margin: -1.5rem;
    margin-bottom: 4.5rem;
    padding: 0;
}

.content > * {
    width: 100%;
    margin: 1.5rem;
}

.content-text {
    display: flex;
    flex-direction: column;

    font-size: 1.85rem;
    color: #52555C;

    line-height: 150%;
}

.content-text > * {
    margin: 0;
    margin-bottom: 1.35rem;
}

.content-text > *:last-child {
    margin-bottom: 0;
}

.content-text b {
    color: #282C35;
}

.content-text-bold {
    font-weight: bold;
    font-size: 2.1rem;
}

.content-logo {
    width: 100%;
    max-width: 175px;
    height: auto;
}

.content-logo img {
    display: block;

    width: 100%;
    height: 100%;

    object-fit: contain;

    filter: unset;
}

.actions {
    display: flex;
    flex-direction: column;
}

.action__row {
    width: 100%;

    display: flex;
    justify-content: center;
    align-items: center;

    text-align: center;

    margin-bottom: 2rem;
}

.actions .action__row:last-child {
    margin-bottom: 0;
}

.btn {
    padding: 1rem 2.9rem;

    cursor: pointer;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 1.3125rem;
    text-decoration: none;
    text-align: left;

    color: #fafafa;
    background-color: #282C35;
    border-radius: 15px;

    border: 0;

    transition: .3s ease;
}

.btn span {
    margin-right: 1.5rem;
}

.btn .icon {
    width: 35px;
    height: 28px;

    color: #fafafa;

    opacity: 1;
}

.btn .icon svg {
    width: 100%;
    height: 100%;

    display: block;

    object-fit: contain;
}

.btn .icon svg,
.btn .icon path {
    fill: currentColor;
}

.btn:hover,
.btn:focus-within {
    opacity: 0.6;
}

.btn--blue {
    background-color: #0088CC;
}

.under-text {
    font-size: 1.125rem;
    margin: 0;

    color: #282C35;

    text-align: center;
}

@media (max-width: 768px) {
  .content {
    margin-bottom: 2.5rem;
  }

  .title {
    font-size: 2rem;
    line-height: 1.2;
  }

  .title span {
    margin-bottom: 1rem;
  }

  .title b {
    padding: 0.6rem 1.5rem;

    font-size: 0.9em;
  }

  .content-text {
    font-size: 1.4rem;
  }

  .content-text-bold {
    font-size: 1.8rem;
  }

  .content-text > * {
    margin-bottom: 1rem;
  }

  .content-logo {
    max-width: 125px;
  }

  .btn {
    padding: 0.9rem 1.2rem;
  }

  .action__row .btn {
    width: 100%;

    justify-content: center;
  }
}

@media (min-width: 768px) {
  .content {
    flex-wrap: nowrap;
    justify-content: space-between;

    text-align: left;
  }

  .content > * {
    width: unset;
  }
}

</style>
