class FormAutosave {
    id = -1;
    form = document.createElement('form');
    postsData = JSON.parse(localStorage.getItem('postsData')) || [];
    storageData = this.postsData.find(el => el.id === this.id);
    saveDelay = 7000;
    lastTryedSavedData = {};
    ignorefillInputNames = [
        'csrfmiddlewaretoken',
    ];

    constructor (element, saveDelay = this.saveDelay, ignorefillInputNames = this.ignorefillInputNames) {

        if (!element) {
            this.id = undefined;
            return;
        }

        this.form = element;
        this.id = this.getPostId();
        this.saveDelay = saveDelay;
        this.ignorefillInputNames = ignorefillInputNames;
    }

    init () {
        if (!this.id) return;

        this.initSavedData();
        this.initIntervalSave();

        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.deleteSavedData();
            e.target.submit();
        })
    }

    async initIntervalSave () {
        setInterval(() => {
            this.saveData()
        }, this.saveDelay);
    }

    initSavedData () {
        this.updateDataByStorage();

        const storageData = this.storageData?.data;
        const formValues = Object.values(this.form);

        if (!storageData || this.isEqualData(storageData, this.getData())) {
            return;
        }

        if (!confirm('Найдены старые данные, загрузить ?')) {
            return;
        }

        for (let i = 0; i < Object.keys(storageData).length; i++) {
            const key = Object.keys(storageData)[i];

            if (this.ignorefillInputNames.includes(key)) continue;

            const input = formValues.find(el => el.name == key);

            if (input) {
                input.value = storageData[key]
            }
        }
    }

    saveData () {
        this.updateDataByStorage();

        const postsData = this.postsData;
        const storageData = this.storageData;
        const curData = this.getData();

        if (!storageData) {
            postsData.push({
                id: this.id,
                data: curData,
            })

            localStorage.setItem('postsData', JSON.stringify(postsData));
            return;
        }

        if (this.isEqualData(storageData.data, curData)) return;

        postsData[postsData.findIndex(el => el.id === this.id)].data = this.getNewPostsData(storageData.data, curData);
        localStorage.setItem('postsData', JSON.stringify(postsData));
    }

    getData () {
        const formValue = Object.values(this.form).reduce((obj,field) => {

            if (field.name && field.name.length) {
                obj[field.name] = field.value
            }

            return obj

        }, {});

        const mdEditor = this.form.querySelector('.markdown-editor-full');

        if (mdEditor) {
            formValue['md'] = mdEditor.value;
        }

        return formValue;
    }

    deleteSavedData () {
        this.updateDataByStorage();

        const newPostsData = JSON.parse(JSON.stringify(this.postsData));
        const deleteIndex = newPostsData.findIndex(el => el.id == this.id);

        if (deleteIndex == -1) return;

        newPostsData.splice(deleteIndex, 1);
        localStorage.setItem('postsData', JSON.stringify(newPostsData));
    }

    updateDataByStorage () {
        this.postsData = JSON.parse(localStorage.getItem('postsData')) || [];
        this.storageData = this.postsData.find(el => el.id === this.id);
    };

    getPostId () {
        const path = document.location.pathname.split('/').filter(el => el.length);
        let curPath = null;

        if (path.length < 2) {
            return curPath;
        }

        const curPathItem = path[path.length - 1];
        const previousPathItem = path[path.length - 2];

        // Check typeof path "create/posts"
        if (previousPathItem === 'create') {
            curPath = path.join('/');
        }

        // Check typeof path "posts/11/edit"
        if (path.length > 2 && !isNaN(previousPathItem) && curPathItem === 'edit') {
            curPath = path.join('/');
        }

        return curPath;
    }

    getNewPostsData (postsData = {}, curData) {
        const result = JSON.parse(JSON.stringify(postsData));

        this.lastTryedSavedData = curData;

        for (let i = 0; i < Object.keys(curData).length; i++) {
            const key = Object.keys(curData)[i];
            const val = curData[key];

            if (!(key in result)) {
                result[key] = val;
                continue;
            }

            if (val.toString().length || this.lastTryedSavedData[key] === val) {
                result[key] = val;
            }
        }

        return result;
    }

    isEqualData (first, second) {
        if (Object.keys(first).length !== Object.keys(second).length) {
            return false;
        }

        let isNotEqualKeys = Object.keys(first).filter(key => first[key] !== second[key]);

        if (isNotEqualKeys.length == 1 && this.ignorefillInputNames.includes(isNotEqualKeys[0])) {
            return true;
        }

        return isNotEqualKeys.length == 0;
    }
}

setTimeout(initComposeFormSaveData, 1000);

// Fucntions
function initComposeFormSaveData () {
    const composeForms = document.querySelectorAll('.compose-form');

    composeForms.forEach((form) => {
        const formObj = new FormAutosave(form);
        formObj.init();
    })
}
