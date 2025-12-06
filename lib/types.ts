export type UserRole = "student" | "admin" | "cost_sharing_officer" | "inland_revenue_officer" | "registrar_officer"

export interface User {
  id: string
  email: string
  password: string
  firstName: string
  lastName: string
  role: UserRole
  studentId?: string
  department?: string
  phoneNumber?: string
  tin?: string
  createdAt: string
  rememberToken?: string
}

export interface CostSharingAgreement {
  id: string
  studentId: string
  studentName: string
  department: string
  yearOfStudy: number
  totalAmount: number
  paidAmount: number
  status: "pending" | "approved" | "rejected"
  submittedAt: string
  reviewedAt?: string
  reviewedBy?: string
  rejectionReason?: string
  personalInfo: {
    dateOfBirth: string
    gender: string
    nationality: string
    region: string
    zone: string
    woreda: string
    kebele: string
  }
  educationalBackground: {
    previousSchool: string
    graduationYear: string
    cgpa: string
  }
  withdrawalTransfer?: {
    hasWithdrawn: boolean
    withdrawalDate?: string
    reason?: string
  }
}

export interface Payment {
  id: string
  studentId: string
  studentName: string
  agreementId: string
  amount: number
  paymentMethod: "bank_transfer" | "mobile_money" | "cash"
  bankAccountId?: string
  transactionReference: string
  receiptUrl?: string
  tin: string
  status: "pending" | "verified" | "rejected"
  submittedAt: string
  verifiedAt?: string
  verifiedBy?: string
  rejectionReason?: string
}

export interface BankAccount {
  id: string
  bankName: string
  accountNumber: string
  accountName: string
  branch: string
  isActive: boolean
  createdAt: string
}

export interface Notice {
  id: string
  title: string
  content: string
  targetRole: UserRole | "all"
  postedBy: string
  postedAt: string
  expiresAt?: string
}

export interface Feedback {
  id: string
  studentId: string
  studentName: string
  subject: string
  message: string
  response?: string
  respondedBy?: string
  respondedAt?: string
  status: "pending" | "responded"
  submittedAt: string
}

export interface CostStructure {
  id: string
  department: string
  yearOfStudy: number
  totalAmount: number
  installments: number
  createdAt: string
  updatedAt: string
}

export interface StudentData {
  id: string
  studentId: string
  firstName: string
  lastName: string
  email: string
  department: string
  yearOfStudy: number
  phoneNumber: string
  uploadedAt: string
  uploadedBy: string
}
