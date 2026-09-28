import { NetworkError, sendFile } from './transport'

export async function upload(file: File) {
    try {
        return await sendFile(file)
    } catch (error) {
        if (error instanceof NetworkError) {
            return sendFile(file)
        }
        throw error
    }
}
