<template>
<main>
    <header>
        <h2>About this app</h2>
    </header>
    <section>
        <h3>
            Built using following technologies:
            </h3>
        <ul>
            <li>
                Vue</li>
            <li>
                Bulma</li>
            <li>
                Vue router</li>
            <li>
                Vuex</li>
            <li>
                Webpack</li>
            <li>
                SocketIO</li>
            <li>
                Flask</li>
            <li>
                UnQLite</li>
            <li>
                Python</li>
            <li>
                GPIO Zero</li>
            </ul>
    </section>
    <section>
        <h3>
            Some quick resources</h3>
        <ul>
            <li>
                <a href="https://github.com/vuejs/awesome-vue" target="_blank">
                    awesome-vue</a>
                </li>
            </ul>
    </section>
</main>
</template>

<script>
export default {
    name: 'about',
    head: { title: { inner: 'About' } }
}
</script>
