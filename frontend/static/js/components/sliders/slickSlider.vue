<template>
  <slick
        ref="slick"

        class="slick-init"
        :class="customClasses"
        :options="curSliderOptions"
    >
        <slot></slot>
    </slick>
</template>

<script>
import Slick from 'vue-slick';

export default {
    components: {
        Slick
    },

    props: {
        sliderOptions: {
            type: Object,
            default: () => {},
        },

        customClasses: {
            type: Array,
            default: () => [],
        }
    },

    data () {
        return {
            curSliderOptions: {},
        }
    },

    mounted () {
        this.curSliderOptions = this.sliderOptions;
        this.reInit();
    },

    methods: {
        reInit() {
            this.$nextTick(() => {
                this.$refs.slick.reSlick();
            });
        },
    },

    watch: {
        sliderOptions (val) {
            if (Object.keys(val).length > 0 && JSON.stringify(val) !== JSON.stringify(this.curSliderOptions)) {
                this.curSliderOptions = val;
                this.reInit();
            }
        }
    }
}
</script>

<style scroped>
.slick-init {
    width: 100%;
}
</style>
