import $ from "jquery";
import moment from "moment";
import daterangepicker from "../plugins/daterangepicker";

const daterangepickerOptions = {
    opens: "right",
    drops: "auto",
    locale: {
        format: "YYYY-MM-DD",
        separator: " - ",
        applyLabel: "Применить",
        cancelLabel: "Закрыть",
        weekLabel: "Нед.",
        daysOfWeek: ["Вс", "Пн", "Пт", "Ср", "Чт", "Пт", "Суб"],
        monthNames: [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ],
        firstDay: 1,
    },
};

const datepicker = () => {
    $(document).ready(() => {
        $('.date-range input[name="date-range"]').each((index, input) => {
            const parent = $(input).parent(".date-range");
            const inputFrom = parent.find('input[name="date_from"]');
            const inputTo = parent.find('input[name="date_to"]');
            const fromVal = inputFrom.val();
            const toVal = inputTo.val();
            const doSubmit = input.dataset.submit;

            // Setup form date inputs
            if (fromVal && toVal) {
                $(input).val(`${fromVal} - ${toVal}`);
            } else {
                inputFrom.val(moment().format("YYYY-MM-DD"));
                inputTo.val(moment().format("YYYY-MM-DD"));
            }

            // Add callback on change
            $(input).daterangepicker(daterangepickerOptions);
            $(input).on('apply.daterangepicker', (e, picker) => {
                inputFrom.val(picker.startDate.format("YYYY-MM-DD"));
                inputTo.val(picker.endDate.format("YYYY-MM-DD"));

                if (!doSubmit) return
                input.closest('form')?.submit();
            })
        });
    });
};

export default datepicker;
