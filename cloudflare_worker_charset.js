export default {
    async fetch(request, env, ctx) {
        const response = await fetch(request);
        const url = new URL(request.url);
        const textExts = ['.md', '.txt', '.json', '.xml', '.csv', '.yaml', '.yml'];
        if (textExts.some(ext => url.pathname.endsWith(ext))) {
            const newHeaders = new Headers(response.headers);
            const contentType = response.headers.get("Content-Type") || "";
            if (
                contentType.startsWith("text/") ||
                contentType.includes("json") ||
                contentType.includes("xml") ||
                contentType.includes("markdown")
            ) {
                const newHeaders = new Headers(response.headers);
                // Принудительно добавляем charset=utf-8
                newHeaders.set(
                    "Content-Type",
                    contentType.replace(/(; ?charset=[^;]*)?/i, "") + "; charset=utf-8"
                );
            }
            return new Response(await response.body, {
                status: response.status,
                statusText: response.statusText,
                headers: newHeaders,
            });
        }
        return response;
    }
}
