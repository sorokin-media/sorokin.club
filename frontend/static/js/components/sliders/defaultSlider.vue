<template>
    <div class="slider-default slider-default--arrows-out" :class="customClasses">
        <div class="slider-default__slider-container">
            <div ref="arrowContainer" class="slider-default__arrows"></div>
            <div class="slider-default__inner">
                <defaultSlider
                    ref="slider"
                    :sliderOptions="sliderOptions"
                    :customClasses="classes"
                >
                    <slot></slot>
                </defaultSlider>
            </div>
        </div>
        <div ref="dotsContainer" class="slider-default__dots"></div>
    </div>
</template>

<script>
import defaultSlider from './slickSlider.vue';

export default {
    components: {
        defaultSlider
    },

    props: {
        customClasses: {
            default: () => [],
        }
    },

    data () {
        return {
            sliderOptions: {
                slidesToShow: 1,
                slidesToScroll: 1,

                dots: true,
                arrows: true,

                appendArrows: this.$refs.arrowContainer,
                appendDots: this.$refs.dotsContainer,

                responsive: [
                    {
                        breakpoint: 1024,
                        settings: {
                            arrows: false,
                        }
                    },
                ]
            },

            classes: ['post-slider'],
        }
    },

    mounted () {
        this.sliderOptions.appendArrows = this.$refs.arrowContainer;
        this.sliderOptions.appendDots = this.$refs.dotsContainer;
    }
}
</script>

<style>

</style>
