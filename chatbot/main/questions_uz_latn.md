# Chatbot uchun test savollari va aniq javoblar

Ushbu 30 ta savol joriy import qilingan manba JSON-laridan semantik SQL ko'rinishlari orqali olingan. Javoblar joriy mahalliy ma'lumotlardagi aniq qiymatlar. Hech qanday taxmin, to'ldirish yoki yo'q qiymatlarni tiklash ishlatilmagan.

## 1. Import qilingan obyektlar soni

**Question:** Joriy import qilingan ma'lumotlar to'plamida nechta viloyat, tuman va mahalla bor?

**Expected answer:** 14 viloyat, 212 tuman, 9088 mahalla.

## 2. Mahalla soni mos kelmaydigan viloyatlar

**Question:** Qaysi viloyatlarda e'lon qilingan mahallalar soni JSON-dagi haqiqiy son bilan mos kelmaydi?

**Expected answer:**

| region_code | region_name_cyr | declared_mahalla_count | actual_mahalla_count |
|---|---|---:|---:|
| 1703 | Андижон вилояти | 879 | 878 |
| 1727 | Тошкент вилояти | 883 | 847 |
| 1730 | Фарғона вилояти | 1015 | 1090 |
| 1733 | Хоразм вилояти | 509 | 543 |
| 1735 | Қорақалпоғистон Республикаси | 452 | 471 |

## 3. Aholisi soni bo'yicha eng yuqori viloyatlar

**Question:** Qaysi 5 viloyat aholisi soni bo'yicha eng yuqori?

**Expected answer:**

| rank | region_name_cyr | population |
|---:|---|---:|
| 1 | Самарқанд вилояти | 4330143 |
| 2 | Фарғона вилояти | 4204055 |
| 3 | Қашқадарё вилояти | 3591291 |
| 4 | Андижон вилояти | 3479657 |
| 5 | Тошкент шаҳри | 3177589 |

## 4. active_businesses bo'yicha eng yuqori viloyatlar

**Question:** Qaysi 5 viloyat active_businesses ko'rsatkichi bo'yicha yetakchi?

**Expected answer:**

| rank | region_name_cyr | active_businesses |
|---:|---|---:|
| 1 | Сурхондарё вилояти | 64606 |
| 2 | Тошкент шаҳри | 58320 |
| 3 | Самарқанд вилояти | 53382 |
| 4 | Андижон вилояти | 44047 |
| 5 | Тошкент вилояти | 29733 |

## 5. Takrorlanuvchi district_code

**Question:** Qaysi district_code bir martadan ko'p uchraydi va aniq qayerda?

**Expected answer:**

| district_code | occurrences | places |
|---:|---:|---|
| 1727413 | 2 | Тошкент вилояти / Бекобод шаҳри; Хоразм вилояти / Ангрен шаҳри |
| 1727415 | 2 | Тошкент вилояти / Оҳангарон шаҳри; Қорақалпоғистон Республикаси / Ангрен шаҳри |
| 1730233 | 2 | Фарғона вилояти / Фарғона тумани; Фарғона вилояти / Фарғона шаҳри |

## 6. Takrorlanuvchi mahalla STIR soni

**Question:** Nechta mahalla STIR qiymati bir martadan ko'p uchraydi?

**Expected answer:** 127 ta STIR qiymati bir martadan ko'p uchraydi.

## 7. Takrorlanuvchi mahalla STIR namunalari

**Question:** Takrorlanuvchi mahalla STIR-larning 5 ta namunasini va ular qayerda uchrashini ko'rsating.

**Expected answer:**

| mahalla_stir | occurrences | places |
|---|---:|---|
| 202824185 | 2 | Тошкент вилояти / Бекобод шаҳри / Қорабоғ; Хоразм вилояти / Ангрен шаҳри / Қорабоғ |
| 202838151 | 2 | Тошкент вилояти / Оҳангарон шаҳри / Гулбоғ; Қорақалпоғистон Республикаси / Ангрен шаҳри / Гулбоғ |
| 202903094 | 2 | Тошкент вилояти / Бекобод шаҳри / Бирдамлик; Хоразм вилояти / Ангрен шаҳри / Бирдамлик |
| 202903103 | 2 | Тошкент вилояти / Бекобод шаҳри / Мукимий; Хоразм вилояти / Ангрен шаҳри / Мукимий |
| 202903110 | 2 | Тошкент вилояти / Бекобод шаҳри / Ал-Хоразмий; Хоразм вилояти / Ангрен шаҳри / Ал-Хоразмий |

## 8. Aholisi soni bo'yicha eng yuqori mahallalar

**Question:** Qaysi 10 mahalla aholisi soni bo'yicha eng yuqori?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | mahalla_name_cyr | population |
|---:|---|---|---|---:|
| 1 | Навоий вилояти | Навоий шаҳри | Фаровон | 22152 |
| 2 | Сурхондарё вилояти | Термиз шаҳри | Боғишамол | 17416 |
| 3 | Тошкент шаҳри | Яшнобод тумани | Боғбон | 16770 |
| 4 | Андижон вилояти | Олтинкўл тумани | Қўштепа | 16381 |
| 5 | Бухоро вилояти | Бухоро шаҳри | Отбозор | 15933 |
| 6 | Қашқадарё вилояти | Қарши тумани | Боғобод | 15836 |
| 7 | Тошкент шаҳри | Мирзо Улуғбек тумани | Авайхон | 15309 |
| 8 | Тошкент шаҳри | Яшнобод тумани | Дўстобод | 15036 |
| 9 | Жиззах вилояти | Жиззах шаҳри | Олмазор | 14202 |
| 10 | Тошкент шаҳри | Яшнобод тумани | Жўрабек | 13552 |

## 9. Eng past mahalla rating_score qiymatlari

**Question:** Qaysi 10 mahalla eng past rating_score qiymatiga ega?

**Expected answer:** Quyidagi 10 mahallaning barchasida rating_score = 1.0.

| region_name_cyr | district_name_cyr | mahalla_name_cyr | rating_score |
|---|---|---|---:|
| Андижон вилояти | Андижон тумани | Янги Андижон | 1.0 |
| Бухоро вилояти | Жондор тумани | Навгади | 1.0 |
| Жиззах вилояти | Зомин тумани | Дуоба | 1.0 |
| Қашқадарё вилояти | Миришкор тумани | Миришкор | 1.0 |
| Навоий вилояти | Зарафшон шаҳри | Ўзбекистон | 1.0 |
| Наманган вилояти | Чортоқ тумани | Бағрикенглик | 1.0 |
| Самарқанд вилояти | Нуробод тумани | Амир Темур | 1.0 |
| Сурхондарё вилояти | Денов тумани | Чоргул | 1.0 |
| Сирдарё вилояти | Ширин шаҳри | Ватанпарвар МФЙ | 1.0 |
| Тошкент шаҳри | Шайхонтохур тумани | Олмазор | 1.0 |

## 10. Mahalla kategoriyasi taqsimoti

**Question:** Har bir category_label_cyr toifasida nechta mahalla bor?

**Expected answer:**

| category_label_cyr | mahalla_count |
|---|---:|
| 3 паст | 4582 |
| 2 ўрта | 2706 |
| 1 юқори | 1800 |

## 11. Mahalla holati taqsimoti

**Question:** Nechta mahallada "Оғир маҳалла" holati mavjud?

**Expected answer:** 9088 mahallada status_label_cyr = "Оғир маҳалла".

## 12. Joriy tuman highlighted qiymati ko'p hollarda yo'q bo'lgan macro indikatorlari

**Question:** Qaysi macro indikatorlar joriy tumanning highlighted qiymatiga eng ko'p hollarda ega emas?

**Expected answer:**

| indicator_key | indicator_label_cyr | missing_count | total_districts |
|---|---|---:|---:|
| investment_growth_pct | Инвестиция ўсиши (%) | 154 | 212 |
| agriculture_growth_pct | Қишлоқ хўжалиги ўсиши (%) | 24 | 212 |
| agriculture_volume_bln | Қишлоқ хўжалиги ҳажми (млрд. сўм) | 24 | 212 |
| export_growth_pct | Экспорт ўсиши (%) | 14 | 212 |
| export_volume_mln_usd | Экспорт ҳажми (млн долл) | 13 | 212 |
| budget_revenue_bln | Бюджетга тушумлар ҳажми (млрд. сўм) | 12 | 212 |
| budget_revenue_growth_pct | Бюджетга тушумлар ўсиши (%) | 12 | 212 |
| industry_growth_pct | Саноат ўсиши (%) | 12 | 212 |
| industry_per_capita_uzs | Саноат аҳоли жон бошига (минг сўм) | 12 | 212 |
| industry_volume_bln_uzs | Саноат ҳажми (млрд. сўм) | 12 | 212 |

## 13. industry_volume_bln_uzs bo'yicha eng yuqori tumanlar

**Question:** Qaysi 10 tuman/shahar industry_volume_bln_uzs bo'yicha eng yuqori qiymatga ega?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | industry_volume_bln_uzs |
|---:|---|---|---:|
| 1 | Навоий вилояти | Навоий шаҳри | 67611.4667952569 |
| 2 | Тошкент вилояти | Олмалиқ шаҳри | 17244.2126174064 |
| 3 | Андижон вилояти | Асака тумани | 10224.2249795669 |
| 4 | Тошкент шаҳри | Яшнобод тумани | 7465.71668230481 |
| 5 | Самарқанд вилояти | Самарқанд шаҳри | 5517.34600102558 |
| 6 | Бухоро вилояти | Қоровулбозор тумани | 4981.93606317455 |
| 7 | Тошкент шаҳри | Чилонзор тумани | 4740.3863569808 |
| 8 | Тошкент шаҳри | Бектемир тумани | 4627.13656266527 |
| 9 | Андижон вилояти | Андижон шаҳри | 4600.87289983429 |
| 10 | Тошкент шаҳри | Сирғали тумани | 4291.44101191521 |

## 14. export_volume_mln_usd bo'yicha eng yuqori tumanlar

**Question:** Qaysi 10 tuman/shahar export_volume_mln_usd bo'yicha eng yuqori qiymatga ega?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | export_volume_mln_usd |
|---:|---|---|---:|
| 1 | Тошкент шаҳри | Учтепа тумани | 109.36873865 |
| 2 | Тошкент шаҳри | Олмазор тумани | 89.908945 |
| 3 | Сурхондарё вилояти | Термиз тумани | 76.630116 |
| 4 | Самарқанд вилояти | Самарқанд шаҳри | 70.496146 |
| 5 | Тошкент шаҳри | Чилонзор тумани | 68.787862 |
| 6 | Тошкент шаҳри | Юнусобод тумани | 58.850884 |
| 7 | Тошкент шаҳри | Сирғали тумани | 56.498304 |
| 8 | Тошкент шаҳри | Янгиҳаёт тумани | 54.520549 |
| 9 | Тошкент шаҳри | Яшнобод тумани | 53.456393 |
| 10 | Тошкент вилояти | Қибрай тумани | 50.282451 |

## 15. road_total_km bo'yicha eng katta qiymatlar

**Question:** Qaysi 10 mahalla road_total_km bo'yicha eng katta qiymatga ega?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | mahalla_name_cyr | road_total_km | road_asphalt_km |
|---:|---|---|---|---:|---:|
| 1 | Тошкент шаҳри | Мирзо Улуғбек тумани | Подшобоғ | 32170.0 | 32170.0 |
| 2 | Тошкент шаҳри | Мирзо Улуғбек тумани | Темурийлар | 16125.0 | 16125.0 |
| 3 | Тошкент шаҳри | Мирзо Улуғбек тумани | Чингелди | 15520.0 | 15520.0 |
| 4 | Тошкент шаҳри | Мирзо Улуғбек тумани | Мунавварқори | 15162.0 | 15162.0 |
| 5 | Тошкент шаҳри | Мирзо Улуғбек тумани | Олтинтепа | 14409.0 | 14409.0 |
| 6 | Тошкент шаҳри | Мирзо Улуғбек тумани | Олмачи | 14058.0 | 14058.0 |
| 7 | Тошкент шаҳри | Мирзо Улуғбек тумани | Алишеробод | 13030.0 | 13030.0 |
| 8 | Тошкент шаҳри | Мирзо Улуғбек тумани | Улуғбек | 13020.0 | 13020.0 |
| 9 | Тошкент шаҳри | Мирзо Улуғбек тумани | Шукур Бурхонов | 12955.0 | 12955.0 |
| 10 | Тошкент шаҳри | Мирзо Улуғбек тумани | Дархон | 12902.0 | 12902.0 |

## 16. road_total_km 1000 dan yuqori bo'lgan mahallalar

**Question:** Nechta mahallada road_total_km 1000 dan katta?

**Expected answer:** 64 mahallada road_total_km > 1000.

## 17. Tibbiyot muassasasigacha bo'lgan eng uzoq masofa

**Question:** Qaysi 10 mahalla medical_facility_distance_km bo'yicha eng katta qiymatga ega?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | mahalla_name_cyr | medical_facility_distance_km |
|---:|---|---|---|---:|
| 1 | Қорақалпоғистон Республикаси | Тахтакўпир тумани | Қоструба МФЙ | 160.0 |
| 2 | Жиззах вилояти | Ғаллаорол тумани | Саврук | 45.0 |
| 3 | Сирдарё вилояти | Мирзаобод тумани | Янги Ўзбекистон | 45.0 |
| 4 | Навоий вилояти | Хатирчи тумани | Ангидон | 40.0 |
| 5 | Самарқанд вилояти | Иштихон тумани | Зарбанд | 36.0 |
| 6 | Сирдарё вилояти | Мирзаобод тумани | Навбахор | 35.0 |
| 7 | Бухоро вилояти | Ғиждувон тумани | Оқработ | 30.0 |
| 8 | Самарқанд вилояти | Иштихон тумани | Бешбола | 27.0 |
| 9 | Самарқанд вилояти | Иштихон тумани | Боғихон | 27.0 |
| 10 | Самарқанд вилояти | Иштихон тумани | Қайирма | 27.0 |

## 18. Viloyatlar bo'yicha jinoyat murojaatlari

**Question:** Qaysi 10 viloyatda crime_appeal_count yig'indisi eng katta?

**Expected answer:**

| rank | region_name_cyr | crime_appeal_count_sum |
|---:|---|---:|
| 1 | Тошкент шаҳри | 2848 |
| 2 | Қашқадарё вилояти | 1691 |
| 3 | Сурхондарё вилояти | 1591 |
| 4 | Самарқанд вилояти | 1392 |
| 5 | Фарғона вилояти | 1373 |
| 6 | Тошкент вилояти | 1333 |
| 7 | Андижон вилояти | 1142 |
| 8 | Наманган вилояти | 843 |
| 9 | Жиззах вилояти | 835 |
| 10 | Бухоро вилояти | 832 |

## 19. Eng yuqori bandlik murojaatlari soni

**Question:** Qaysi 10 mahallada employment_appeal_count eng katta?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | mahalla_name_cyr | employment_appeal_count |
|---:|---|---|---|---:|
| 1 | Тошкент вилояти | Паркент тумани | Новдак | 55 |
| 2 | Навоий вилояти | Навоий шаҳри | Янгиобод | 34 |
| 3 | Бухоро вилояти | Бухоро тумани | Боғикалон | 30 |
| 4 | Навоий вилояти | Зарафшон шаҳри | Мурунтау | 30 |
| 5 | Қашқадарё вилояти | Ғузор тумани | Гулистон | 29 |
| 6 | Навоий вилояти | Навоий шаҳри | Зарафшон | 24 |
| 7 | Навоий вилояти | Учқудуқ тумани | Дўстлик | 24 |
| 8 | Навоий вилояти | Навоий шаҳри | Ватан | 22 |
| 9 | Навоий вилояти | Зарафшон шаҳри | Наврўз | 20 |
| 10 | Навоий вилояти | Зарафшон шаҳри | Қурувчи | 20 |

## 20. divorce_appeal_count bo'yicha ma'lumot yo'q qatorlar

**Question:** Qaysi 10 viloyatda divorce_appeal_count bo'yicha ma'lumoti yo'q qatorlar eng ko'p?

**Expected answer:**

| rank | region_name_cyr | missing_divorce_rows | total_mahallas |
|---:|---|---:|---:|
| 1 | Фарғона вилояти | 866 | 1090 |
| 2 | Самарқанд вилояти | 763 | 1070 |
| 3 | Андижон вилояти | 665 | 878 |
| 4 | Тошкент вилояти | 630 | 847 |
| 5 | Наманган вилояти | 572 | 754 |
| 6 | Қашқадарё вилояти | 502 | 776 |
| 7 | Сурхондарё вилояти | 459 | 723 |
| 8 | Бухоро вилояти | 411 | 516 |
| 9 | Хоразм вилояти | 409 | 543 |
| 10 | Тошкент шаҳри | 408 | 585 |

## 21. Ixtisoslashuv turlari soni

**Question:** Qaysi specialization_type_cyr eng ko'p uchraydi va ularning population_count yig'indisi qancha?

**Expected answer:**

| specialization_type_cyr | rows | population_count_sum |
|---|---:|---:|
| Чорвачилик | 6784 | 7216036.0 |
| Дехқончилик | 5700 | 7100698.0 |
| Савдо ва хизмат кўрсатиш | 4970 | 4151795.0 |
| Кичик ишлаб чиқариш | 2471 | 1319651.0 |
| Боғдочилик | 2038 | 2154234.0 |
| Паррандачилик | 1487 | 715314.0 |
| Ҳунармандчилик | 1028 | 531741.0 |
| Резаворлар | 150 | 140883.0 |

## 22. Aholi bo'yicha eng yuqori ixtisoslashuv yo'nalishlari

**Question:** Qaysi specialization_direction_cyr population_count yig'indisi eng yuqori?

**Expected answer:**

| rank | specialization_direction_cyr | rows | population_count_sum |
|---:|---|---:|---:|
| 1 | Қорамолчилик | 5445 | 5933077.0 |
| 2 | Озиқ-овқат ва ноозиқ овқат савдоси | 2771 | 2252040.0 |
| 3 | Картошкачилик | 1454 | 1894849.0 |
| 4 | Сабзавотчилик | 1569 | 1870589.0 |
| 5 | Хизмат кўрсатиш | 1545 | 1372360.0 |
| 6 | Қўй ва эчкичилик | 1280 | 1243942.0 |
| 7 | Узумчилик | 714 | 1069636.0 |
| 8 | Дуккакли экинлар | 669 | 790145.0 |
| 9 | Тикувчилик | 1337 | 718389.0 |
| 10 | Товуқчилик | 1415 | 687493.0 |

## 23. Ekin mavsumlarida ma'lumot yo'q va manfiy qiymatlar

**Question:** Ekin mavsumlarida nechta total_area_ha qiymati ma'lumot yo'q, jami nechta ekin qatori bor va manfiy homestead_area_ha mavjudmi?

**Expected answer:** total_area_ha bo'yicha ma'lumot yo'q = 22105 / 22105 qator. Manfiy homestead_area_ha qatorlari = 5. Eng kichik homestead_area_ha = -0.0151.

## 24. crop_total_homestead_area_sotkah bo'yicha eng yuqori mahallalar

**Question:** Qaysi 10 mahallada crop_total_homestead_area_sotkah eng yuqori?

**Expected answer:**

| rank | region_name_cyr | district_name_cyr | mahalla_name_cyr | crop_total_homestead_area_sotkah |
|---:|---|---|---|---:|
| 1 | Қашқадарё вилояти | Кўкдала тумани | Ғаллакор | 1379.3384 |
| 2 | Қашқадарё вилояти | Кўкдала тумани | Чувуллок | 1231.1034 |
| 3 | Қашқадарё вилояти | Чироқчи тумани | Ғаллачи | 1166.5044 |
| 4 | Қашқадарё вилояти | Кўкдала тумани | Утамайли | 931.0227 |
| 5 | Қашқадарё вилояти | Кўкдала тумани | Кумдарё | 918.3522 |
| 6 | Қашқадарё вилояти | Кўкдала тумани | Аннарўз | 907.7208 |
| 7 | Қашқадарё вилояти | Кўкдала тумани | Чиял | 889.6227 |
| 8 | Қашқадарё вилояти | Кўкдала тумани | Хардури | 880.3272 |
| 9 | Қашқадарё вилояти | Кўкдала тумани | Гулистон | 867.0009 |
| 10 | Қашқадарё вилояти | Кўкдала тумани | Сой буйи | 823.6076 |

## 25. Subsidiya dasturlari bo'yicha arizalar

**Question:** Subsidiya dasturlari bo'yicha har bir dasturning application_count yig'indisi qancha?

**Expected answer:**

| subsidy_program_label_cyr | rows | application_count_sum | null_application_rows |
|---|---:|---:|---:|
| Уруғлик, кўчат | 6282 | 13096.0 | 3591 |
| Суғориш | 6282 | 10584.0 | 4347 |
| Қуёш панели ўрнатиш | 6282 | 6761.0 | 4033 |
| «Уста-шогирд» дастури | 6282 | 6439.0 | 4331 |
| Кооператив | 6282 | 4718.0 | 5894 |
| Жазони ўтаб келганлар | 6282 | 3102.0 | 5094 |
| Касаначилик (уйда иш) | 6282 | 108.0 | 6213 |
| Ижара тўлови субсидияси | 6282 | 45.0 | 6247 |

## 26. required_amount_mln_uzs bo'yicha ma'lumot yo'q qatorlar

**Question:** Subsidiya dasturlarining nechta qatorida required_amount_mln_uzs bo'yicha ma'lumot yo'q?

**Expected answer:** 50256 ta subsidiya dasturi qatoridan 41999 tasida required_amount_mln_uzs bo'yicha ma'lumot yo'q.

## 27. Eng ko'p uchraydigan peer kuchli factor_key

**Question:** Qaysi peer kuchli factor_key qiymatlari eng ko'p uchraydi?

**Expected answer:**

| rank | factor_key | factor_label_cyr | rows |
|---:|---|---|---:|
| 1 | power_outages_count | Электр узилишлари сони (марта) | 5033 |
| 2 | power_outages_time | Электр узилишлари вақти (минут) | 4448 |
| 3 | internal_dirt_roads_share_percent | Ички тупроқ йўллар улуши | 3763 |
| 4 | drinking_water_with_unsupplied_household_count_per_100_hh | Ичимлик суви билан таъминланмаган хонадонлар сони | 3683 |
| 5 | lonely_elderly_count_1000 | Ёлғиз кексалар сони | 3229 |
| 6 | liqui_date_d_business_entities_count_1000 | Тугатилган тадбиркорлик субъектлари сони | 2825 |
| 7 | material_aid_recipients_count_1000 | Моддий ёрдам олувчилар сони | 1887 |
| 8 | divorces_count_per_100_family | Ажримлар сони | 1603 |
| 9 | crimes_committed_count_1000 | Содир этилган жиноятлар сони | 1540 |
| 10 | troubled_family_count_per_100_family | Нотинч оилалар сони | 1385 |

## 28. Eng ko'p uchraydigan peer zaif factor_key

**Question:** Qaysi peer zaif factor_key qiymatlari eng ko'p uchraydi?

**Expected answer:**

| rank | factor_key | factor_label_cyr | rows |
|---:|---|---|---:|
| 1 | sport_playgrounds_count_per_100_hh | Спорт майдончалари сони | 2936 |
| 2 | with_homestead_plot_households_share_percent | Томорқаси бор хонадонлар улуши | 2552 |
| 3 | total_homestead_plot_area_sotikh_per_100_hh | Умумий томорқа майдони, сотих | 2298 |
| 4 | schools_count_1000 | Мактаблар сони | 2208 |
| 5 | internal_asphalt_roads_share_percent | Ички асфальт (бетон) йўллар улуши | 1990 |
| 6 | preschool_education_institutions_count_1000 | Мактабгача таълим муассасалари сони | 1949 |
| 7 | newly_established_business_entities_count_1000 | Янги ташкил этилган тадбиркорлик субъектлари сони | 1826 |
| 8 | active_business_entities_count_1000 | Фаолият кўрсатаётган тадбиркорлик субъектлари сони | 1773 |
| 9 | inactive_business_entities_count_1000 | Нофаол тадбиркорлик субъектлари сони | 1602 |
| 10 | liqui_date_d_business_entities_count_1000 | Тугатилган тадбиркорлик субъектлари сони | 1418 |

## 29. Ma'lumot sifati muammolari soni

**Question:** Joriy importda qanday data quality issue kodlari bor va ularning soni qancha?

**Expected answer:**

| issue_code | count |
|---|---:|
| MAHALLA_STIR_DUPLICATE | 127 |
| REGION_MAHALLA_COUNT_MISMATCH | 5 |
| DISTRICT_CODE_DUPLICATE_GLOBAL | 3 |
| DISTRICT_CODE_PREFIX_MISMATCH | 3 |

Jami muammolar: 138.

## 30. Viloyat, macro, detail va sifat bo'yicha umumiy tekshiruv

**Question:** Umumiy ko'rsatkichlarni bering: nechta viloyatda mahalla_count_mismatch bor, nechta macro highlighted qiymati ma'lumot yo'q, nechta mahallada road_total_km > 1000, nechta ekin qatorida manfiy homestead_area_ha bor va jami nechta data quality muammosi mavjud?

**Expected answer:**

| metric | value |
|---|---:|
| regions_with_mahalla_count_mismatch | 5 |
| macro_highlights_missing | 373 |
| mahallas_with_road_total_km_gt_1000 | 64 |
| crop_rows_with_negative_homestead_area_ha | 5 |
| data_quality_issues_total | 138 |
