import { sendFile } from './transport'

export async function upload(file: File) {
    return sendFile(file)
}
