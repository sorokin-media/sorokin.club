document.addEventListener("DOMContentLoaded", function () {
  const tables = document.querySelectorAll('table');

  tables.forEach((table) => {
    const isDefault = table.classList.length == 0;

    if (isDefault) {
        createWrapper (table, 'div', ['d-table']);
    }
  })
});

function createWrapper (el, tag = '', classList = []) {
    const wrapper = document.createElement(tag);
    const innerElement = el.cloneNode(true);

    classList.forEach(className => {
        wrapper.classList.add(className);
    });

    wrapper.appendChild(innerElement);
    el.insertAdjacentElement('beforeBegin', wrapper);
    el.remove();
}
