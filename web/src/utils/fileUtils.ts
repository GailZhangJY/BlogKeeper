/**
 * 从 content-disposition 响应头中提取文件名
 * @param contentDisposition content-disposition 响应头的值
 * @returns 解码后的文件名
 */
export function getFileNameFromContentDisposition(contentDisposition: string): string {
    // 检查是否包含 filename* 参数
    const filenameMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (filenameMatch) {
        // 解码 URL 编码的文件名
        return decodeURIComponent(filenameMatch[1]);
    }
    
    // 如果没有 filename*，尝试获取普通的 filename
    const regularFilenameMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
    if (regularFilenameMatch) {
        return regularFilenameMatch[1];
    }
    
    return '';
}

/**
 * 从响应头中获取文件名
 * @param response Fetch API 的响应对象
 * @returns 文件名
 */
export function getFileNameFromResponse(response: Response): string {
    const contentDisposition = response.headers.get('content-disposition');
    if (!contentDisposition) return '';
    
    return getFileNameFromContentDisposition(contentDisposition);
}

/**
 * 从响应头中解析文件名的接口
 */
export interface FileNameParser {
    /**
     * 从响应中获取文件名
     * @param response Fetch API 的响应对象
     */
    getFileName(response: Response): string;
}

/**
 * 默认的文件名解析器实现
 */
export class DefaultFileNameParser implements FileNameParser {
    getFileName(response: Response): string {
        return getFileNameFromResponse(response);
    }
}
