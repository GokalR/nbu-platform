/**
 * Demo seeds — pre-filled Step 1 + Step 2 answers for showcase runs.
 *
 * The seed mirrors a typical education center SME in Margilan — the base
 * template in rs-step5-i18n.js is already tailored for this scenario.
 *
 * Option strings MUST match exactly the values declared in
 * rs-step1-i18n.js / rs-step2-i18n.js (ru variants) — otherwise the
 * RsSelectField shows an empty value.
 */

export const DEMO_SEEDS = {
  erkinParvoz: {
    label: 'Учебный центр (Маргилан)',
    ru: {
      profile: {
        name: 'SMART EDUCATION MCHJ',
        ageRange: '31-40',
        gender: 'Мужской',
        hasHigherEducation: 'Да',
        educationField: 'IT и программирование',
        maritalStatus: 'Женат/Замужем',
        dependents: '1-2',
        currentStatus: 'Предприниматель',
        experienceLevel: '3-5 лет',
        domainExperience: 'Да, работал(а) в этой сфере',
        hasTraining: 'Да',
        hasMentor: 'Нет',
        viloyat: 'Ферганская область',
        hudud: 'Марғилон шаҳар',
        mahalla: 'Бахрин',
        urbanRural: 'Город',
        entityType: 'Юридическое лицо',
        registrationForm: 'ООО',
        businessSize: 'Малый (5–25 сотрудников)',
        businessAge: '3–5 лет',
        employeeCount: '6–15',
      },
      finance: {
        businessDirection: 'Учебный центр',
        ideaDescription:
          'Действующий учебный центр IT-направления в Маргилане. 1 филиал, 6 преподавателей, ~80 студентов. Планируем открыть второй филиал в махалле Бахрин с фокусом на AI/ML, data science и кибербезопасность.',
        whyThisBusiness: 'Есть опыт в этой сфере',
        targetCustomer: 'Физические лица (B2C)',
        hasOwnFunds: 'Да',
        hasSpace: 'Да, арендую',
        hasEquipment: 'Частично',
        hasRegisteredBusiness: 'Да, ООО',
        hasBusinessPlan: 'Есть черновик',
        needsLoan: 'Да, обязательно',
        timeline: 'В течение 1 месяца',
        monthlyIncome: '50–100 млн',
        monthlyExpenses: '30–50 млн',
        existingDebt: 'Нет',
        businessGoal: 'Открыть новую точку',
        mainProblem: 'Не хватает оборотных средств',
        loanAmount: '200–500 млн',
        hasCollateral: 'Да',
        collateralType: 'Дом / квартира',
      },
    },
    uz: {
      profile: {
        name: 'SMART EDUCATION MCHJ',
        ageRange: '31-40',
        gender: 'Erkak',
        hasHigherEducation: 'Ha',
        educationField: 'IT va dasturlash',
        maritalStatus: 'Turmush qurgan',
        dependents: '1-2',
        currentStatus: 'Predprinimatel',
        experienceLevel: '3-5 yil',
        domainExperience: 'Ha, bu sohada ishlaganman',
        hasTraining: 'Ha',
        hasMentor: 'Yoʻq',
        viloyat: 'Ferganskaya oblast',
        hudud: 'Margʻilon shahar',
        mahalla: 'Bahrin',
        urbanRural: 'Shahar',
        entityType: 'Yuridicheskoe litso',
        registrationForm: 'MChJ',
        businessSize: 'Kichik (5–25 xodim)',
        businessAge: '3–5 yil',
        employeeCount: '6–15',
      },
      finance: {
        businessDirection: 'Oʻquv markazi',
        ideaDescription:
          'Margʻilonda IT yoʻnalishidagi amaldagi oʻquv markazi. 1 filial, 6 oʻqituvchi, ~80 talaba. Bahrin mahallasida AI/ML, data science va kiber xavfsizlik yoʻnalishlarida ikkinchi filial ochishni rejalashtirmoqdamiz.',
        whyThisBusiness: 'Bu sohada tajribam bor',
        targetCustomer: 'Jismoniy shaxslar (B2C)',
        hasOwnFunds: 'Ha',
        hasSpace: 'Ha, ijarada',
        hasEquipment: 'Qisman',
        hasRegisteredBusiness: 'Ha, MChJ',
        hasBusinessPlan: 'Qoralama bor',
        needsLoan: 'Ha, albatta',
        timeline: '1 oy ichida',
        monthlyIncome: '50–100 mln',
        monthlyExpenses: '30–50 mln',
        existingDebt: 'Yoʻq',
        businessGoal: 'Yangi filial ochish',
        mainProblem: 'Aylanma mablagʻ etishmaydi',
        loanAmount: '200–500 mln',
        hasCollateral: 'Ha',
        collateralType: 'Uy / kvartira',
      },
    },
  },
}
