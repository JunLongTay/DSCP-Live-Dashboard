import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import Papa from 'papaparse'
import * as XLSX from 'xlsx'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export async function loadCsv(url: string): Promise<any[]> {
  const response = await fetch(url)
  const csvText = await response.text()

  return new Promise((resolve, reject) => {
    Papa.parse(csvText, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => resolve(results.data as any[]),
      error: (err: Error) => reject(err)
    })
  })
}

export async function loadExcel(url: string, maxRows = 100): Promise<any[]> {
  const res = await fetch(url)
  const buffer = await res.arrayBuffer()
  const workbook = XLSX.read(buffer, { type: 'array' })

  const firstSheet = workbook.SheetNames[0]
  const worksheet = workbook.Sheets[firstSheet]

  // Determine how far to read: A1 to full row range
  const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1:Z1000')
  range.e.r = Math.min(range.e.r, maxRows - 1) // limit rows to maxRows
  worksheet['!ref'] = XLSX.utils.encode_range(range)

  const partialData = XLSX.utils.sheet_to_json(worksheet)
  return partialData
}