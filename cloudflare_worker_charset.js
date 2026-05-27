export default {
    async fetch(request, env, ctx) {
        const response = await fetch(request);
        const contentType = response.headers.get("Content-Type") || "";
        if (
            contentType.startsWith("text/") ||
            contentType.includes("json") ||
            contentType.includes("xml") ||
            contentType.includes("markdown")
        ) {
            const newHeaders = new Headers(response.headers);
            newHeaders.set(
                "Content-Type",
                contentType.replace(/(; ?charset=[^;]*)?/i, "") + "; charset=utf-8"
            );
            return new Response(response.body, {
                status: response.status,
                statusText: response.statusText,
                headers: newHeaders,
            });
        }
        return response;
    },
};
