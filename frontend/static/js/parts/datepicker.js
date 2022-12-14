import $ from "jquery";
import moment from "moment";
import daterangepicker from "daterangepicker";

const daterangepickerOptions = {
    opens: 'right',
    drops: "auto",
    locale: {
        format: "YYYY-MM-DD",
        separator: " - ",
        applyLabel: 'Применить',
        cancelLabel: 'Закрыть',
        weekLabel: "Нед.",
        daysOfWeek: [
            "Вс",
            "Пн",
            "Пт",
            "Ср",
            "Чт",
            "Пт",
            "Суб"
        ],
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
            "Декабрь"
        ],
        firstDay: 1
    }
}

const datepicker = () => {
    $(document).ready(() => {
        $('.date-range input[name="dates"]').each((index, input) => {

            const parent = $(input).parent('.date-range');
            const inputFrom = parent.find('input[name="date_from"]');
            const inputTo = parent.find('input[name="date_to"]');

            $(input).daterangepicker(
                daterangepickerOptions,
                (start, end) => {
                    inputFrom.val(start.format('YYYY-MM-DD'))
                    inputTo.val(end.format('YYYY-MM-DD'));
                }
            );

        });
    })
}

export default datepicker;
