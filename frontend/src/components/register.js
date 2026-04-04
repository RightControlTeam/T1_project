import router from '@/router'
import api from '@/api'


export function validate_form(form, valid_errors) {
    valid_errors.value.username = ""
    valid_errors.value.password = ""
    let is_valid = true
    if (!form.value.username) {
        valid_errors.value.username = "Логин обязателен!"
        is_valid = false
    }
    else if (form.value.username.length < 5 || form.value.username.length > 25) {
        valid_errors.value.username = "Длина логина должна быть от 5 до 25 символов!"
        is_valid = false
    }
    else if (!/^\w+$/.test(form.value.username)) {
        valid_errors.value.username = "Логин может содержать только буквы, цифры и нижнее подчёркивание"
        is_valid = false
    }
    else if (/^[0-9_]/.test(form.value.username)) {
        valid_errors.value.username = "Логин не может начинаться с цифры или нижнего подчёркивания"
        is_valid = false
    }

    if (!form.value.password) {
        valid_errors.value.password = "Пароль обязателен!"
        is_valid = false
    }
    else if (form.value.password.length < 8 || form.value.password.length > 40) {
        valid_errors.value.password = "Длина пароля должна быть от 8 до 40 символов"
        is_valid = false
    }
    return is_valid
};


export async function register(validate_form, path, form, error, valid_errors) {
  console.log('Аргументы:', { validate_form, path, form, error, valid_errors })

  console.log('=== register.js ===')
  console.log('validate_form:', typeof validate_form)
  console.log('path:', path)
  console.log('form:', form)
  console.log('error:', error)
  console.log('error:', valid_errors)
  console.log('valid_errors:', valid_errors.value.username, valid_errors.value.password)
  console.log('error?.value:', error.value.msg, error.value.status)
  error.value.msg = ""
  error.value.status = ""
  if (validate_form(form, valid_errors)) {
    try {
        const response = await api.post(path, form.value)
        console.log('Данные отправлены')
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('admin_level', response.data.admin_level)
        console.log(response.data)
        form.value.username = ''
        form.value.password = ''
        console.log('success')
        if (response.data.admin_level == 0) {
            router.push('/')
        }
    }
    catch (e) {
        if (!e.response) {
            error.value.msg = 'Сервер не отвечает'
            console.log('response: ', e.response)
        } else {
            error.value.status = e.response.status
            console.log(e)
            console.log(`Статус ошибки ${error.value.status}`)
            if (error.value.status == 409) {
                error.value.msg = 'Такой логин уже существует'
            } else {
                error.value.msg = 'Произошла ошибка'
            }
        }
    }
  }
}