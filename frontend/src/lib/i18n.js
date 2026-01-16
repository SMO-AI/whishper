import { writable, derived } from 'svelte/store';

export const locale = writable('ru'); // Default to Russian

const translations = {
    en: {
        settings: 'Settings',
        profile: 'Profile',
        edit_profile: 'Edit Profile',
        logout: 'Logout',
        check_subscription: 'Check Subscription',
        theme_light: 'Light',
        theme_dark: 'Dark',
        general: 'General',
        language: 'Language',
        save: 'Save',
        cancel: 'Cancel',
        full_name: 'Full Name',
        password: 'Password',
        new_password: 'New Password',
        update_password: 'Update Password',
        avatar: 'Avatar',
        upload_avatar: 'Upload Avatar',
        success_profile_updated: 'Profile updated successfully',
        success_password_updated: 'Password updated successfully',
        error_updating: 'Error updating profile',
        your_library: 'Your Library',
        manage_explore: 'Manage and explore your transcriptions',
        new_transcription: 'New Transcription',
        uploading: 'Uploading',
        collection_empty: 'Your collection is empty',
        start_uploading: 'Start by uploading your first audio file',
        success: 'Success',
        error: 'Error',
        pending: 'Pending',
        translating: 'Translating',
        download: 'Download',
        translate: 'Translate',
        delete: 'Delete'
    },
    ru: {
        settings: 'Настройки',
        profile: 'Профиль',
        edit_profile: 'Редактировать профиль',
        logout: 'Выйти',
        check_subscription: 'Подписка',
        theme_light: 'Светлая',
        theme_dark: 'Темная',
        general: 'Общие',
        language: 'Язык',
        save: 'Сохранить',
        cancel: 'Отмена',
        full_name: 'Имя',
        password: 'Пароль',
        new_password: 'Новый пароль',
        update_password: 'Обновить пароль',
        avatar: 'Аватар',
        upload_avatar: 'Загрузить фото',
        success_profile_updated: 'Профиль успешно обновлен',
        success_password_updated: 'Пароль успешно обновлен',
        error_updating: 'Ошибка обновления профиля',
        your_library: 'Ваша библиотека',
        manage_explore: 'Управляйте и изучайте ваши транскрипции',
        new_transcription: 'Новая запись',
        uploading: 'Загрузка',
        collection_empty: 'Ваша коллекция пуста',
        start_uploading: 'Начните с загрузки вашего первого аудиофайла',
        success: 'Готово',
        error: 'Ошибка',
        pending: 'В обработке',
        translating: 'Перевод',
        download: 'Скачать',
        translate: 'Перевести',
        delete: 'Удалить'
    }
};

export const t = derived(locale, ($locale) => (key) => {
    const translation = translations[$locale] && translations[$locale][key];
    return translation || translations['en'][key] || key;
});
