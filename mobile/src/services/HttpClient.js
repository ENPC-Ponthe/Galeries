import axios from "axios";
import DeviceStorage from "./DeviceStorage";

export const BASE_URL = 'http://192.168.1.38:5000'
// export const BASE_URL = 'https://ponthe.enpc.org'


export const url = (path: string, prefix: string = '') => {
    return BASE_URL + prefix + path
}


export const get = async (path: string, onFetch,  prefix: string = '/api') => {
    try {
        const jwt = await DeviceStorage.getJWT()
        let response = await fetch(
            url(path, prefix), {
                headers: new Headers({
                    'Authorization': 'Bearer ' + jwt,
                }),
            }
        )
        let data = await response.json()

        console.debug(data)

        onFetch(data)
    } catch (error) {
        console.error(error)
    }
}


export const post = async (path: string, body, onFetch) => {
    try {
        let response = await axios.post(url(path, '/api'), body)
        onFetch(response)
    } catch (error)  {
        console.log(error)
    }
}
