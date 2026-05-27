export default {
    async fetch(request, env, ctx) {
        const response = await fetch(request);
        const url = new URL(request.url);
        const textExts = ['.md', '.txt', '.json', '.xml', '.csv', '.yaml', '.yml'];
        if (textExts.some(ext => url.pathname.endsWith(ext))) {
            const newHeaders = new Headers(response.headers);
            let contentType = newHeaders.get('content-type') || 'text/plain';
            if (!contentType.includes('charset')) {
                if (url.pathname.endsWith('.json')) contentType = 'application/json';
                else if (url.pathname.endsWith('.xml')) contentType = 'application/xml';
                else if (url.pathname.endsWith('.md')) contentType = 'text/markdown';
                else if (url.pathname.endsWith('.txt')) contentType = 'text/plain';
                else if (url.pathname.endsWith('.csv')) contentType = 'text/csv';
                else if (url.pathname.endsWith('.yaml') || url.pathname.endsWith('.yml')) contentType = 'text/yaml';
                contentType += '; charset=utf-8';
                newHeaders.set('content-type', contentType);
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
