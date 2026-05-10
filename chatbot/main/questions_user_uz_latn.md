# Realistic user questions (Uzbek Latin)

These cases mirror how real users actually phrase questions: no column names, no
SQL jargon, mixed everyday vocabulary. Expected answers focus on **facts a
correct system must surface**, not exact prose. The scorer checks numeric facts
and the missing-value marker; it does not enforce wording.

## 1. Salom

**Question:** Salom

**Expected answer:** Assalomu alaykum. Men viloyat, tuman va mahalla statistikasi bo'yicha savollarga javob beraman.

## 2. Capability

**Question:** Nimalarni so'rashim mumkin?

**Expected answer:** Viloyatlar bo'yicha aholi, biznes, ishsizlik va reyting; tumanlar bo'yicha sanoat, eksport, investitsiya va byudjet; mahallalar bo'yicha infratuzilma, murojaatlar, ixtisoslashuv va subsidiyalar; ma'lumot sifati muammolari.

## 3. Top viloyatlar aholi soni bo'yicha

**Question:** Qaysi viloyatlarda aholi eng ko'p?

**Expected answer:** Eng yuqori aholisi bo'lgan viloyatlar (taxminan 5 ta), real qiymatlari bilan, kamayuvchi tartibda. Manba: v_regions.population.

## 4. Eng past reytingli mahallalar

**Question:** Mahallalar reytingi eng past bo'lgan joylarni ko'rsat.

**Expected answer:** Eng past `rating_score` qiymatiga ega 10 ta mahalla, viloyat va tuman nomi bilan. Bo'sh qiymatlar `ma'lumot yo'q` deb belgilanadi, 0 emas.

## 5. Yo'l infratuzilmasi

**Question:** Yo'l infratuzilmasi eng katta ko'rsatkichga ega mahallalar qaysilar?

**Expected answer:** `road_total_km` bo'yicha eng katta 10 ta mahalla, yonida `road_asphalt_km` qiymati. Bo'sh qiymat — `ma'lumot yo'q`.

## 6. Tibbiyot masofasi

**Question:** Tibbiyot muassasasigacha masofa eng uzoq bo'lgan mahalla qaysi?

**Expected answer:** Eng katta `medical_facility_distance_km` qiymatiga ega bitta yoki bir nechta mahalla, viloyat/tuman nomlari bilan.

## 7. Jinoyat murojaatlari viloyatlar bo'yicha

**Question:** Qaysi viloyatlarda jinoyat bo'yicha murojaatlar ko'p?

**Expected answer:** `crime_appeal_count` yig'indisi bo'yicha viloyatlar reytingi (kamayuvchi). Yig'indi mahallalardan olinadi.

## 8. Subsidiya dasturlari

**Question:** Subsidiya arizalari bo'yicha qaysi dasturlar faol?

**Expected answer:** `subsidy_program_label_cyr` bo'yicha guruhlangan, `application_count` yig'indisi kamayuvchi tartibda. Eng faol bir nechta dastur ko'rinadi.

## 9. Sanoat hajmi tumanlari

**Question:** Sanoat hajmi eng yuqori tumanlarni ko'rsat.

**Expected answer:** `industry_volume_bln_uzs` bo'yicha eng katta 10 ta tuman, viloyat nomi bilan, kamayuvchi tartibda.

## 10. Takror STIR

**Question:** Ma'lumotlarda takror STIR bormi?

**Expected answer:** `v_data_quality_issues` ichida `MAHALLA_STIR_DUPLICATE` bo'yicha topilgan ishlar soni. Agar 0 bo'lsa, "takror STIR yo'q" deyiladi.

## 11. Eksport hajmi

**Question:** Eksport hajmi bo'yicha eng yuqori tumanlar qaysi?

**Expected answer:** `export_volume_mln_usd` bo'yicha eng katta tumanlar, kamayuvchi tartibda, viloyat nomi bilan.

## 12. Mahalla ixtisoslashuvi

**Question:** Qaysi mahallalar nimaga ixtisoslashgan?

**Expected answer:** `specialization_type_cyr` va `specialization_direction_cyr` bo'yicha eng ko'p uchraydigan toifalar va ularga to'g'ri keluvchi mahallalar soni.

## 13. Out-of-scope

**Question:** Toshkentda bugun ob-havo qanday?

**Expected answer:** Bot ob-havo ma'lumotlarini saqlamasligini va faqat viloyat/tuman/mahalla statistikasi bo'yicha javob berishini bildiradi.
