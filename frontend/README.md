src/
├── components/     # Переиспользуемые компоненты
│   ├── LoginForm.vue
│   ├── ResourceCard.vue
│   └── ...
├── views/          # Страницы
│   ├── HomePage.vue
│   ├── LoginPage.vue
│   └── ...
├── router/         # Маршрутизация
├── stores/         # Состояние (Pinia)
├── api/            # Запросы к бэкенду
└── utils/          # Вспомогательные функции


| Метод   | URL             | Описание        |
|---------|-----------------|-----------------|
| POST    | /user/login/    | Вход            |
| POST    | /user/register/ | Регистрация     |
| GET     | /user/profile/  | Профиль         |
| GET     | /resources/     | Список ресурсов |
| POST    | /bookings/      | Создать бронь   |
| GET     | /bookings/my/   | Мои брони       |

## 🎨 Компоненты для реализации

1. **LoginPage** - страница входа
2. **RegisterPage** - страница регистрации
3. **ResourcesPage** - список ресурсов
4. **BookingForm** - форма бронирования
5. **MyBookingsPage** - мои брони
6. **NavBar** - навигация

```
#Frontend запустить
cd frontend
nmp install
npm run dev
```
