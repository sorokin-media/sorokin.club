<template>
  <div class="reviews-item">
        <div class="reviews-item__avatar">
            <img :src="'/static/' + data.avatarSrc" alt="">
        </div>
        <div class="reviews-item__main">
            <div class="reviews-item__header">
                <div class="reviews-item__title-container">
                    <div class="reviews-item__avatar">
                        <img :src="'/static/' + data.avatarSrc" alt="">
                    </div>
                    <div class="reviews-item__title">
                        <div class="reviews-item__name">{{ data.name }}</div>
                        <div class="reviews-item__position">{{ data.position }}</div>
                    </div>
                </div>

                <div v-if="data.achive" class="reviews-item__achive">
                    <ul class="reviews-item__achive-list">
                        <li
                            v-for="achiveItem in achiveList"
                            :key="achiveItem"
                        >
                            {{ achiveItem }}
                        </li>
                    </ul>
                </div>
            </div>

            <div class="reviews-item__body">
                <div class="reviews-item__review">
                    <div v-if="data.review" ref="review" class="reviews-item__text" :class="{ 'hidden' : isTextHidden }">
                        <template v-for="(text, index) in reviewText">
                            <p v-if="text.length" :key="index">
                                {{ text }}
                            </p>
                        </template>
                    </div>
                    <button v-if="hideTextLogic" @click="toggleReview" type="button" class="reviews-item__read-more">

                        <template v-if="isTextHidden">
                            Читать полностью
                        </template>

                        <template v-else>
                            Скрыть
                        </template>

                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        data: {
            default: () => {},
        }
    },

    data () {
        return {
            hideTextLogic: false,
            isTextHidden: false,
            maxReviewHeight: 270,
        }
    },

    computed: {
        reviewText () {
            if (!this.data.review) {
                return '';
            }

            return this.data.review.split('\n').filter((line) => line.replace(/\s/gm, '').length > 0);
        },

        achiveList () {
            if (!this.data.achive) {
                return '';
            }

            return this.data.achive.split('\n').filter((line) => line.replace(/\s/gm, '').length > 0);
        }
    },

    beforeMount () {
        window.addEventListener('resize', this.checkReviewHeight);
    },

    mounted () {
        this.maxReviewHeight = parseInt(window.getComputedStyle(this.$refs.review).maxHeight.replace(/\D/gm, ''));
        this.setupCheckReviewHeight();
    },

    beforeDestroy () {
        window.removeEventListener('resize', this.checkReviewHeight);
    },

    methods: {

        setupCheckReviewHeight () {
            if (this.$refs.review.scrollHeight > this.maxReviewHeight) {
                this.hideTextLogic = true;
                this.isTextHidden = true;
           } else {
                this.hideTextLogic = false
                this.isTextHidden = false;
           }
        },

        checkReviewHeight () {

            if (this.$refs.review.scrollHeight > this.maxReviewHeight) {

                if (!this.isTextHidden && this.hideTextLogic) {
                    this.$refs.review.style.maxHeight = this.$refs.review.scrollHeight + 'px';
                }

                if (!this.hideTextLogic) {
                    this.hideTextLogic = true;
                    this.isTextHidden = true;
                }

            } else {
                this.hideTextLogic = false;
                this.isTextHidden = false;
            }

        },

        toggleReview () {
            if (!this.isTextHidden) {
                this.$refs.review.style.maxHeight = this.maxReviewHeight + 'px';
            } else {
                this.$refs.review.style.maxHeight = this.$refs.review.scrollHeight + 'px';
            }

            this.isTextHidden = !this.isTextHidden;
        }

    }
}
</script>

<style>

</style>
