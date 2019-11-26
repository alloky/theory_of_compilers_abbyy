class TreeVisitor{
    public static void main(String[] a){
        System.out.println(new TV().Start()); // HERE privateMethod
    }
}

class TV {

    private int f(){
        return 0;
    }

    public int Start() {
        return this.f() + 1;
    }

}

