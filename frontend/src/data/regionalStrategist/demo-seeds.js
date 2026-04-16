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
        hasSpace: 'Нет, нужна аренда',
        hasEquipment: 'Частично',
        hasRegisteredBusiness: 'Да, ООО',
        hasBusinessPlan: 'Есть черновик',
        needsLoan: 'Да, обязательно',
        timeline: 'В течение 1 месяца',
        monthlyIncome: '50–100 млн',
        monthlyExpenses: '30–50 млн',
        existingDebt: 'Нет',
        businessGoal: 'Основные средства',
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
        gender: 'Эркак',
        hasHigherEducation: 'Ҳа',
        educationField: 'IT ва дастурлаш',
        maritalStatus: 'Турмуш қурган',
        dependents: '1-2',
        currentStatus: 'Предприниматель',
        experienceLevel: '3-5 йил',
        domainExperience: 'Ҳа, бу соҳада ишлаганман',
        hasTraining: 'Ҳа',
        hasMentor: 'Йўқ',
        viloyat: 'Ферганская область',
        hudud: 'Марғилон шаҳар',
        mahalla: 'Баҳрин',
        urbanRural: 'Шаҳар',
        entityType: 'Юридическое лицо',
        registrationForm: 'МЧЖ',
        businessSize: 'Кичик (5–25 ходим)',
        businessAge: '3–5 йил',
        employeeCount: '6–15',
      },
      finance: {
        businessDirection: 'Ўқув маркази',
        ideaDescription:
          'Марғилонда IT йўналишидаги амалдаги ўқув маркази. 1 филиал, 6 ўқитувчи, ~80 талаба. Баҳрин маҳалласида AI/ML, data science ва кибер хавфсизлик йўналишларида иккинчи филиал очишни режалаштирмоқдамиз.',
        whyThisBusiness: 'Бу соҳада тажрибам бор',
        targetCustomer: 'Жисмоний шахслар (B2C)',
        hasOwnFunds: 'Ҳа',
        hasSpace: 'Йўқ, ижара керак',
        hasEquipment: 'Қисман',
        hasRegisteredBusiness: 'Ҳа, МЧЖ',
        hasBusinessPlan: 'Қоралама бор',
        needsLoan: 'Ҳа, албатта',
        timeline: '1 ой ичида',
        monthlyIncome: '50–100 млн',
        monthlyExpenses: '30–50 млн',
        existingDebt: 'Йўқ',
        businessGoal: 'Асосий воситалар',
        mainProblem: 'Айланма маблағ етишмайди',
        loanAmount: '200–500 млн',
        hasCollateral: 'Ҳа',
        collateralType: 'Уй / квартира',
      },
    },
  },
}
