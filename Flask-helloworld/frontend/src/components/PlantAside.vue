<template>
<aside>
    <section>
        <h3>Interests...</h3>
        <ul>
            <li>Show tank</li>
            <li>Water statistics</li>
            <li>Configure</li>
        </ul>
    </section>
</aside>
</template>

<script>
export default { name: 'plan-aside' }
</script>

<style scoped>
aside {
    float : left;
    width : 150px;
    margin-right: 20px;
    margin-bottom : 15px;
    background-color : #D0D0D0 ;
    padding : 5px;
    border : 1px solid #A8A8A8;
}
ul {
    list-style-type: none;
    padding: 0;
}
section * {
    text-align: left;
}
</style>
