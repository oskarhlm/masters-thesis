type RequestOptions = {
  method: string;
  headers?: HeadersInit;
  body?: BodyInit | null;
};

const port = import.meta.env.VITE_BACKEND_PORT;
export const BASE_URL = `http://127.0.0.1:${port || 8000}`;

async function fetchAPI(endpoint: string, options: RequestOptions) {
  const url = `${BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Fetch API error:', error);
    throw error;
  }
}

export async function get(endpoint: string, queryParams?: Record<string, any>) {
  const queryString = queryParams
    ? '?' + new URLSearchParams(queryParams).toString()
    : '';

  return fetchAPI(endpoint + queryString, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });
}

export async function post(endpoint: string, data: any) {
  return fetchAPI(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

export async function put(endpoint: string, data: any) {
  return fetchAPI(endpoint, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
}

export async function del(endpoint: string) {
  return fetchAPI(endpoint, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
}
