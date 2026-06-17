export const apiFetch = async (url, options = {}) => {
  let token = localStorage.getItem("accessToken");
  
  if (!options.headers) {
    options.headers = {};
  }
  
  if (token) {
    options.headers["Authorization"] = `Bearer ${token}`;
  }

  let response = await fetch(url, options);

  if (response.status === 401 && token) {
    const refreshToken = localStorage.getItem("refreshToken");
    if (refreshToken) {
      try {
        const refreshRes = await fetch("http://localhost:8000/api/auth/token/refresh/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh: refreshToken })
        });

        if (refreshRes.ok) {
          const data = await refreshRes.json();
          localStorage.setItem("accessToken", data.access);
          options.headers["Authorization"] = `Bearer ${data.access}`;
          // Retry original request with new token
          response = await fetch(url, options);
        } else {
          window.dispatchEvent(new Event('auth:logout'));
        }
      } catch (err) {
        window.dispatchEvent(new Event('auth:logout'));
      }
    } else {
      window.dispatchEvent(new Event('auth:logout'));
    }
  }

  return response;
};
