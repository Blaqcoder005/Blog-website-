const API_BASE =import.meta.env.VITE_API_URL;

export async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });

    console.log('Response status:', res.status);
    console.log('Response headers:', res.headers);

    if (!res.ok) {
      const text = await res.text();
      console.log('Error response:', text);
      throw new Error(`API error: ${res.status} - ${text}`);
    }

    return res.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

