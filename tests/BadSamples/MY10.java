class TreeVisitor{
    public static void main(String[] a){
        System.out.println(0);
    }
}

class TV1 {
}

class TV {
    public int Start(){
        TV a;
        a = new TV1();  // HERE wrongType
        return 0 ;
    }

}
