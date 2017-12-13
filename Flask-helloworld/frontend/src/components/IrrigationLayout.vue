<template>
<main class="content clearfix">
    <header>
        <h1 class="toptitle">
            <router-link :to="{name: 'plantwatcher'}">
                Plant Irrigation Module
            </router-link>
        </h1>
    </header>
    <aside>
        <section>
            <h4>Interests...</h4>
            <ul class="list-inline">
                <li><a href="#">Show tank</a></li>
                <li><a href="#">Water statistics</a></li>
                <li><router-link :to="{name: 'plantmanager'}">
                    Manage service
                </router-link></li>
            </ul>
        </section>
    </aside>
    <slot/>
</main>
</template>

<script>
export default {
    name: 'irrigation-layout'
}
</script>

<style scoped>
main > aside {
    float: left;
    margin: 0 1.2%;
    width: 16.7%;
    background-color : #D0D0D0 ;
    border: 1px solid #A8A8A8;
    border-radius: 15px;
    padding-top: 10px;
    padding-left: 10px;
    padding-bottom: 10px;
    text-align: left;
    white-space: nowrap;
}
main > aside h4 {
    margin: 0 auto 15px 0;
}
main > aside ul {
    margin: 0;
}
main > section {
    float: right;
    width: 74.7%;
    margin: 0 1.2%;
    border: 1px solid lightgrey;
    border-radius: 15px;
    padding: 0 10px;
}
</style>
