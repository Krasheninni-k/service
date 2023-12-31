# service
Общая логика работы приложения:

Шаг 1. Закупка (форма 1)
1.1. Вносится информация о закупке: номер, дата, кол-во наименований.
1.2. Далее эта информация передается через GET-запрос в форму ввода деталей закупки.

Шаг 2. Детали закупки (форма 2)
2.1. Вносится информация о составе закупки. Заполняется форма по каждому наименованию: продукт, количество, себест, цена в юанях.
2.2. Создается объект закупки (модель Orders): 4 поля (3 поля формы 1 +  кем создан)
2.3. На каждое наименование товара создается по объекту деталей закупки (модель OrderDetail):
    - 3 поля FK (номер, дата закупки, дата получения);
    - 5 полей (4 поля формы 2 + кем создан).
2.4. В объект закупки дозаписывается составное поле список товаров.
2.5. На каждый товар каждого наименования создается по объекту товара (модель Goods):
    - 4 поля FK Orders (номер закупки, дата закупки, дата получения, кем создан);
    - 3 поля FK OrderDetail (продукт, себест, цена в юанях).
2.6. По каждому наименованию обновляется данные каталога (модель Catalog):
    - 2 поля (расчетная цена от себеста, расчетная цена от курса валюты).
2.7. В объект закупки дозаписывается расчетное поле итоговая цена.

Шаг 3. Получение закупки (форма 3)
3.1. Вносится информация о дате получения закупки.
3.2. В объект закупки дозаписывается дата получения. В других моделях инфа обновится автоматически (связь FK)

Шаг 4. Продажа (форма 4)
4.1. Вносится информация о продаже: номер, дата, кол-во наименований, тип покупателя, имя, способ оплаты, способ доставки.
4.2. Далее эта информация передается через GET-запрос в форму ввода деталей продажи.

Шаг 5. Детали продажи (форма 5)
5.1. Вносится информация о составе продажи. Заполняется форма по каждому наименованию: продукт, количество, цена
5.2. Создается объект продажи (модель Sales): 8 полей (7 полей формы 4 +  кем создан)
5.3. На каждое наименование товара создается по объекту деталей продажи (модель SaleDetail):
    - 2 поля FK (номер, дата продажи);
    - 4 поля (3 поля формы 5 + кем создан).
5.4. В объект продажи дозаписывается составное поле список товаров.
5.5. На каждый товар каждого наименования (модель Goods) дозаписываются поля:
    - 1 поле FK Sales (дата продажи);
    - 1 поле FK SaleDetail (цена продажи);
    - 3 расчетных поля (дни на складе, маржа, наценка).
5.6. В объект продажи дозаписывается расчетное поле итоговая цена.

Шаг 6. Изменение данных закупки (форма 6)
6.1. Вносятся новые данные о закупке: номер, дата закупки, дата получения
    !!! ЕСЛИ НУЖНО ИСПРАВИТЬ КОЛ-ВО НАИМЕНОВАНИЙ - ЗАКУПКУ НУЖНО УДАЛИТЬ И СОЗДАТЬ НОВУЮ!
6.2. Внесенные данные перезаписываются в объект закупки (модель Orders).
6.3. Для каждого ПРОДАННОГО наименования каждого товара перезаписывается поле дни на складе.

Шаг 7. Изменение деталей закупки (форма 7)
7.1. Вносятся новые данные о деталях закупки: продукт, себест, цена в юанях.
    !!! ЕСЛИ НУЖНО ИСПРАВИТЬ КОЛ-ВО ТОВАРОВ - ЗАКУПКУ НУЖНО УДАЛИТЬ И СОЗДАТЬ НОВУЮ!
7.2. Внесенные данные перезаписываются в объект деталей закупки (модель OrderDetail).
7.3. В объекте закупки (модель Orders) перезаписывается составное поле список товаров.
7.4. В каждом объекте товара (модель Goods) перезаписываются поля маржа и наценка.
7.5. В объекте закупки (модель Orders) перезаписывается расчетное поле итоговая цена.

Шаг 8. Изменеие данных продажи (форма 8)
8.1. Вносятся новые данные о продаже: номер, дата, тип покупателя, имя, способ оплаты, способ доставки.
    !!! ЕСЛИ НУЖНО ИСПРАВИТЬ КОЛ-ВО НАИМЕНОВАНИЙ - ПРОДАЖУ НУЖНО УДАЛИТЬ И СОЗДАТЬ НОВУЮ!
8.2. Внесенные данные перезаписываются в объект продажи (модель Sales).
8.3. Для каждого ПРОДАННОГО наименования каждого товара перезаписывается поле дни на складе.

Шаг 9. Изменение деталей продажи (форма 9)
9.1. Вносятся новые данные о деталях продажи: продукт, цена продажи
    !!! ЕСЛИ НУЖНО ИСПРАВИТЬ КОЛ-ВО ТОВАРОВ - ПРОДАЖУ НУЖНО УДАЛИТЬ И СОЗДАТЬ НОВУЮ!
9.2. Внесенные данные перезаписываются в объект деталей продажи (модель SaleDetail).
9.3. В объекте продажи (модель Sales) перезаписывается составное поле список товаров.
9.4. В каждом объекте товара (модель Goods) перезаписываются поля маржа и наценка.
9.5. В объекте продажи (модель Sales) перезаписывается расчетное поле итоговая цена.

Шаг 10. Изменение настроек (форма - 10. Курс валюты)
10.1. Вносится информаиця о новом курсе юаня. Заполняется форма 10.
10.2. Внесенные данные перезаписываются в объект настроек (модель CustomSettings).
10.3. В каждом объекте каталога (модель Catalog) перезаписывается значение расчетной цены от курса валюты.

Шаг 11. Изменение настроек (форма - 10. Издержки на доставку, нормативы наценки)
??? объединить с п.10. перезаписывать и поле расчетная цена от себеста

Прочее:

