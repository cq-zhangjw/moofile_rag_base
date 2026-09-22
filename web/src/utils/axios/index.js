
import axios from 'axios';


console.log(import.meta.env.VITE_API_BASE)
const axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE,
    timeout: 0
});


axiosInstance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => {
        console.error('请求错误:', error);
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    response => {
        return response;
    },
    error => {
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    // 处理未授权情况，例如跳转到登录页
                    console.log('未授权，请登录');
                    break;
                case 404:
                    break;
                case 500:
                    break;
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;