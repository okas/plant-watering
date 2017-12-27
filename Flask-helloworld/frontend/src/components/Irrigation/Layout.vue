<template>
<main class="content clearfix">
    <header>
        <h1 class="toptitle">
            <router-link :to="{name: 'irrigation'}">
                Plant Irrigation Module
            </router-link>
        </h1>
    </header>
    <aside id="irrigation_aside">
        <section>
            <h4>Interests...</h4>
            <ul class="list-style-none">
                <li><a href="">Show tank</a></li>
                <li><a href="">Water statistics</a></li>
                <li><router-link :to="{name: 'irrigationservice'}">
                    Manage service
                </router-link></li>
            </ul>
        </section>
        <section>
            <h4>Service state</h4>
            <ul class="list-style-none">
                <li>Service: <span class="highlight">on</span></li>
                <li>Water level: <span class="highlight">low</span></li>
            </ul>
        </section>
    </aside>
    <slot/>
</main>
</template>

<script>
export default { name: 'IrrigationLayout' }
</script>

<style scoped>
.content > aside {
    float: left;
    margin: 0 1.0%;
    width: 14.0%;
    background-color : #effcf8;
    border: 1px solid #A8A8A8;
    border-radius: 15px;
    padding: 10px;
    text-align: left;
    white-space: nowrap;
}
.content > aside h4 {
    margin: 0 auto 5% 0;
}
.content > aside ul {
    margin: 0;
}
aside > section:not(:first-child) {
    margin-top: 12.5%;
    padding-top: 10px;
    border-top: 1px solid #A8A8A8;
}
.content > section {
    float: right;
    width: 77.4%;
    margin: 0 1.0%;
    border: 1px solid lightgrey;
    border-radius: 15px;
    padding: 0 10px 10px;
}
</style>
