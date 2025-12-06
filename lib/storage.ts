import type {
  User,
  CostSharingAgreement,
  Payment,
  BankAccount,
  Notice,
  Feedback,
  CostStructure,
  StudentData,
} from "./types"

// LocalStorage keys
const KEYS = {
  USERS: "ocsms_users",
  AGREEMENTS: "ocsms_agreements",
  PAYMENTS: "ocsms_payments",
  BANK_ACCOUNTS: "ocsms_bank_accounts",
  NOTICES: "ocsms_notices",
  FEEDBACK: "ocsms_feedback",
  COST_STRUCTURES: "ocsms_cost_structures",
  STUDENT_DATA: "ocsms_student_data",
  CURRENT_USER: "ocsms_current_user",
  REMEMBER_TOKEN: "ocsms_remember_token",
}

// Generic storage functions
function getFromStorage<T>(key: string): T[] {
  if (typeof window === "undefined") return []
  const data = localStorage.getItem(key)
  return data ? JSON.parse(data) : []
}

function saveToStorage<T>(key: string, data: T[]): void {
  if (typeof window === "undefined") return
  localStorage.setItem(key, JSON.stringify(data))
}

// Initialize with demo data
export function initializeStorage() {
  if (typeof window === "undefined") return

  // Check if already initialized
  if (localStorage.getItem(KEYS.USERS)) return

  // Create demo users
  const demoUsers: User[] = [
    {
      id: "1",
      email: "admin@mau.edu.et",
      password: "admin123",
      firstName: "Admin",
      lastName: "User",
      role: "admin",
      createdAt: new Date().toISOString(),
    },
    {
      id: "2",
      email: "student@mau.edu.et",
      password: "student123",
      firstName: "John",
      lastName: "Doe",
      role: "student",
      studentId: "MAU/2024/001",
      department: "Computer Science",
      phoneNumber: "+251911234567",
      tin: "TIN001234567",
      createdAt: new Date().toISOString(),
    },
    {
      id: "3",
      email: "costofficer@mau.edu.et",
      password: "cost123",
      firstName: "Cost",
      lastName: "Officer",
      role: "cost_sharing_officer",
      createdAt: new Date().toISOString(),
    },
    {
      id: "4",
      email: "inland@mau.edu.et",
      password: "inland123",
      firstName: "Inland",
      lastName: "Officer",
      role: "inland_revenue_officer",
      createdAt: new Date().toISOString(),
    },
    {
      id: "5",
      email: "registrar@mau.edu.et",
      password: "registrar123",
      firstName: "Registrar",
      lastName: "Officer",
      role: "registrar_officer",
      createdAt: new Date().toISOString(),
    },
  ]

  // Create demo bank accounts
  const demoBankAccounts: BankAccount[] = [
    {
      id: "1",
      bankName: "Commercial Bank of Ethiopia",
      accountNumber: "1000123456789",
      accountName: "Mekdela Amba University",
      branch: "Addis Ababa",
      isActive: true,
      createdAt: new Date().toISOString(),
    },
    {
      id: "2",
      bankName: "Bank of Abyssinia",
      accountNumber: "2000987654321",
      accountName: "Mekdela Amba University",
      branch: "Bahir Dar",
      isActive: true,
      createdAt: new Date().toISOString(),
    },
  ]

  // Create demo cost structures
  const demoCostStructures: CostStructure[] = [
    {
      id: "1",
      department: "Computer Science",
      yearOfStudy: 1,
      totalAmount: 15000,
      installments: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    {
      id: "2",
      department: "Computer Science",
      yearOfStudy: 2,
      totalAmount: 18000,
      installments: 3,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
  ]

  saveToStorage(KEYS.USERS, demoUsers)
  saveToStorage(KEYS.BANK_ACCOUNTS, demoBankAccounts)
  saveToStorage(KEYS.COST_STRUCTURES, demoCostStructures)
  saveToStorage(KEYS.AGREEMENTS, [])
  saveToStorage(KEYS.PAYMENTS, [])
  saveToStorage(KEYS.NOTICES, [])
  saveToStorage(KEYS.FEEDBACK, [])
  saveToStorage(KEYS.STUDENT_DATA, [])
}

// User functions
export const userStorage = {
  getAll: () => getFromStorage<User>(KEYS.USERS),
  getById: (id: string) => getFromStorage<User>(KEYS.USERS).find((u) => u.id === id),
  getByEmail: (email: string) => getFromStorage<User>(KEYS.USERS).find((u) => u.email === email),
  create: (user: User) => {
    const users = getFromStorage<User>(KEYS.USERS)
    users.push(user)
    saveToStorage(KEYS.USERS, users)
  },
  update: (id: string, updates: Partial<User>) => {
    const users = getFromStorage<User>(KEYS.USERS)
    const index = users.findIndex((u) => u.id === id)
    if (index !== -1) {
      users[index] = { ...users[index], ...updates }
      saveToStorage(KEYS.USERS, users)
    }
  },
  delete: (id: string) => {
    const users = getFromStorage<User>(KEYS.USERS).filter((u) => u.id !== id)
    saveToStorage(KEYS.USERS, users)
  },
}

// Agreement functions
export const agreementStorage = {
  getAll: () => getFromStorage<CostSharingAgreement>(KEYS.AGREEMENTS),
  getById: (id: string) => getFromStorage<CostSharingAgreement>(KEYS.AGREEMENTS).find((a) => a.id === id),
  getByStudentId: (studentId: string) =>
    getFromStorage<CostSharingAgreement>(KEYS.AGREEMENTS).filter((a) => a.studentId === studentId),
  create: (agreement: CostSharingAgreement) => {
    const agreements = getFromStorage<CostSharingAgreement>(KEYS.AGREEMENTS)
    agreements.push(agreement)
    saveToStorage(KEYS.AGREEMENTS, agreements)
  },
  update: (id: string, updates: Partial<CostSharingAgreement>) => {
    const agreements = getFromStorage<CostSharingAgreement>(KEYS.AGREEMENTS)
    const index = agreements.findIndex((a) => a.id === id)
    if (index !== -1) {
      agreements[index] = { ...agreements[index], ...updates }
      saveToStorage(KEYS.AGREEMENTS, agreements)
    }
  },
}

// Payment functions
export const paymentStorage = {
  getAll: () => getFromStorage<Payment>(KEYS.PAYMENTS),
  getById: (id: string) => getFromStorage<Payment>(KEYS.PAYMENTS).find((p) => p.id === id),
  getByStudentId: (studentId: string) =>
    getFromStorage<Payment>(KEYS.PAYMENTS).filter((p) => p.studentId === studentId),
  getByAgreementId: (agreementId: string) =>
    getFromStorage<Payment>(KEYS.PAYMENTS).filter((p) => p.agreementId === agreementId),
  create: (payment: Payment) => {
    const payments = getFromStorage<Payment>(KEYS.PAYMENTS)
    payments.push(payment)
    saveToStorage(KEYS.PAYMENTS, payments)
  },
  update: (id: string, updates: Partial<Payment>) => {
    const payments = getFromStorage<Payment>(KEYS.PAYMENTS)
    const index = payments.findIndex((p) => p.id === id)
    if (index !== -1) {
      payments[index] = { ...payments[index], ...updates }
      saveToStorage(KEYS.PAYMENTS, payments)
    }
  },
}

// Bank Account functions
export const bankAccountStorage = {
  getAll: () => getFromStorage<BankAccount>(KEYS.BANK_ACCOUNTS),
  getById: (id: string) => getFromStorage<BankAccount>(KEYS.BANK_ACCOUNTS).find((b) => b.id === id),
  getActive: () => getFromStorage<BankAccount>(KEYS.BANK_ACCOUNTS).filter((b) => b.isActive),
  create: (account: BankAccount) => {
    const accounts = getFromStorage<BankAccount>(KEYS.BANK_ACCOUNTS)
    accounts.push(account)
    saveToStorage(KEYS.BANK_ACCOUNTS, accounts)
  },
  update: (id: string, updates: Partial<BankAccount>) => {
    const accounts = getFromStorage<BankAccount>(KEYS.BANK_ACCOUNTS)
    const index = accounts.findIndex((b) => b.id === id)
    if (index !== -1) {
      accounts[index] = { ...accounts[index], ...updates }
      saveToStorage(KEYS.BANK_ACCOUNTS, accounts)
    }
  },
}

// Notice functions
export const noticeStorage = {
  getAll: () => getFromStorage<Notice>(KEYS.NOTICES),
  getById: (id: string) => getFromStorage<Notice>(KEYS.NOTICES).find((n) => n.id === id),
  getByRole: (role: string) => {
    const notices = getFromStorage<Notice>(KEYS.NOTICES)
    return notices.filter((n) => n.targetRole === role || n.targetRole === "all")
  },
  create: (notice: Notice) => {
    const notices = getFromStorage<Notice>(KEYS.NOTICES)
    notices.push(notice)
    saveToStorage(KEYS.NOTICES, notices)
  },
  delete: (id: string) => {
    const notices = getFromStorage<Notice>(KEYS.NOTICES).filter((n) => n.id !== id)
    saveToStorage(KEYS.NOTICES, notices)
  },
}

// Feedback functions
export const feedbackStorage = {
  getAll: () => getFromStorage<Feedback>(KEYS.FEEDBACK),
  getById: (id: string) => getFromStorage<Feedback>(KEYS.FEEDBACK).find((f) => f.id === id),
  getByStudentId: (studentId: string) =>
    getFromStorage<Feedback>(KEYS.FEEDBACK).filter((f) => f.studentId === studentId),
  create: (feedback: Feedback) => {
    const feedbacks = getFromStorage<Feedback>(KEYS.FEEDBACK)
    feedbacks.push(feedback)
    saveToStorage(KEYS.FEEDBACK, feedbacks)
  },
  update: (id: string, updates: Partial<Feedback>) => {
    const feedbacks = getFromStorage<Feedback>(KEYS.FEEDBACK)
    const index = feedbacks.findIndex((f) => f.id === id)
    if (index !== -1) {
      feedbacks[index] = { ...feedbacks[index], ...updates }
      saveToStorage(KEYS.FEEDBACK, feedbacks)
    }
  },
}

// Cost Structure functions
export const costStructureStorage = {
  getAll: () => getFromStorage<CostStructure>(KEYS.COST_STRUCTURES),
  getById: (id: string) => getFromStorage<CostStructure>(KEYS.COST_STRUCTURES).find((c) => c.id === id),
  getByDepartment: (department: string) =>
    getFromStorage<CostStructure>(KEYS.COST_STRUCTURES).filter((c) => c.department === department),
  create: (structure: CostStructure) => {
    const structures = getFromStorage<CostStructure>(KEYS.COST_STRUCTURES)
    structures.push(structure)
    saveToStorage(KEYS.COST_STRUCTURES, structures)
  },
  update: (id: string, updates: Partial<CostStructure>) => {
    const structures = getFromStorage<CostStructure>(KEYS.COST_STRUCTURES)
    const index = structures.findIndex((c) => c.id === id)
    if (index !== -1) {
      structures[index] = { ...structures[index], ...updates }
      saveToStorage(KEYS.COST_STRUCTURES, structures)
    }
  },
}

// Student Data functions
export const studentDataStorage = {
  getAll: () => getFromStorage<StudentData>(KEYS.STUDENT_DATA),
  getById: (id: string) => getFromStorage<StudentData>(KEYS.STUDENT_DATA).find((s) => s.id === id),
  getByStudentId: (studentId: string) =>
    getFromStorage<StudentData>(KEYS.STUDENT_DATA).find((s) => s.studentId === studentId),
  create: (student: StudentData) => {
    const students = getFromStorage<StudentData>(KEYS.STUDENT_DATA)
    students.push(student)
    saveToStorage(KEYS.STUDENT_DATA, students)
  },
  bulkCreate: (students: StudentData[]) => {
    const existing = getFromStorage<StudentData>(KEYS.STUDENT_DATA)
    saveToStorage(KEYS.STUDENT_DATA, [...existing, ...students])
  },
}

// Auth functions
export const authStorage = {
  getCurrentUser: () => {
    if (typeof window === "undefined") return null
    const userData = localStorage.getItem(KEYS.CURRENT_USER)
    return userData ? JSON.parse(userData) : null
  },
  setCurrentUser: (user: User | null) => {
    if (typeof window === "undefined") return
    if (user) {
      localStorage.setItem(KEYS.CURRENT_USER, JSON.stringify(user))
    } else {
      localStorage.removeItem(KEYS.CURRENT_USER)
    }
  },
  getRememberToken: () => {
    if (typeof window === "undefined") return null
    return localStorage.getItem(KEYS.REMEMBER_TOKEN)
  },
  setRememberToken: (token: string | null) => {
    if (typeof window === "undefined") return
    if (token) {
      localStorage.setItem(KEYS.REMEMBER_TOKEN, token)
    } else {
      localStorage.removeItem(KEYS.REMEMBER_TOKEN)
    }
  },
}

// Unified storage export for convenience
export const storage = {
  getAgreements: agreementStorage.getAll,
  getPayments: paymentStorage.getAll,
  getBankAccounts: bankAccountStorage.getAll,
  getNotices: noticeStorage.getAll,
  getFeedback: feedbackStorage.getAll,
  getCostStructures: costStructureStorage.getAll,
  getStudentData: studentDataStorage.getAll,
  agreements: agreementStorage,
  payments: paymentStorage,
  bankAccounts: bankAccountStorage,
  notices: noticeStorage,
  feedback: feedbackStorage,
  costStructures: costStructureStorage,
  studentData: studentDataStorage,
  users: userStorage,
  auth: authStorage,
}
