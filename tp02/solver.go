package main

import . "fmt"
import . "strconv"
import . "gonum.org/v1/gonum/mat"
import (
	"math"
	"math/rand"
	"os"
	"runtime"
	 "bufio"
	"time"
)

var DEBUG = 0
var ASSERTS = 1

type Ins struct {
	custo      []float64
	capacidade []float64
	x          []float64
	y          []float64
	distancias [][]float64
}

type Cli struct {
	demanda    []float64
	x          []float64
	y          []float64
	distancias [][]float64
}

type Sol struct {
	conectar       []int // Representa um cliente (index) conectado à instalação (valor)
	distancia      float64
	custo          []float64
	custototal     float64 // Custo de abertura das instalações desta solução 	- Minimizar isso
	demanda		  []float64
	estouroudemanda bool
}

var numClientes int
var numInstalacoes int
var ClientesZeros []int
var InstalacoesZeros []float64
var ClientesIndex []int
var InstalacoesIndex []int

/*
    instance_list = ['fl_25_2', 'fl_50_6', 'fl_100_7', 'fl_100_1', 'fl_200_7', 'fl_500_7',
                     'fl_1000_2', 'fl_2000_2']
    good_values = [4000000, 4500000, 2050, 26000000, 5000000, 30000000,
                   10000000, 10000000]
    great_values = [3269822, 3732794, 1966, 22724066, 4711295, 27006099,
                    8879294, 7453531]
*/
func main() {

	
	
	if len(os.Args) <= 1 {
		Printf("\nUso: solver <file>\n")
		os.Exit(1)
	}
	

	rand.Seed(time.Now().UTC().UnixNano())

	i,j,Fi,Ci,Dj,Distancias := load(os.Args[1])
	
	Xij := NewDense(i,j,nil)
	
	for Iteracoes := 100000000; Iteracoes > 0; Iteracoes-- {

		
		
		
		
		
	}
}


func load(path string) (int, int, *Dense, *Dense , *Dense, *Dense) {

	var i 	int
	var j 	int
	var Fi 	*Dense
	var Ci 	*Dense
	var Ixy *Dense
	var Dj 	*Dense
	var Cxy *Dense
	var Distancias *Dense
	var a,b,c,d float64

	file, err := os.Open(path)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	Fscanf(file, "%d %d\n", &i, &j)

	if DEBUG > 0 {
		Printf("Instalações: %d\nClientes: %d\n", i, j)
	}

	Fi = NewDense(1,i,nil)
	Ci = NewDense(1,i,nil)
	Ixy = NewDense(i,2,nil)
	Distancias = NewDense(i,j,nil)

	for ii := 0; ii < ii; ii++ {		
		Fscanf(file, "%f %f %f %f\n", &a, &b, &c, &d)
		Fi.Set(0,ii,a)
		Ci.Set(0,ii,b)
		Ixy.Set(ii,0,c)
		Ixy.Set(ii,1,d)
	}
	
	for jj := 0; j < j; jj++ {
	
		Fscanf(file, "%f %f %f\n", &a, &b, &c)
		
		Dj.Set(0,jj,a)
		Cxy.Set(jj,0,b)
		Cxy.Set(jj,1,c)
	}

	for c := 0; c < j; c++ {
		for i := 0; i < i; i++ {
			Distancias.Set(i,j, math.Sqrt(math.Pow(Cxy.At(c,0)-Ixy.At(i,0), 2) + math.Pow(Cxy.At(c,1)-Ixy.At(i,1), 2)))
		}
	}

	return 	i,j,Fi,Ci,Dj,Distancias
}

func Memory() string {

	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	//fmt.Printf("Alloc = %v MiB", bToMb(m.Alloc))
	//fmt.Printf("\tTotalAlloc = %v MiB", bToMb(m.TotalAlloc))
	//fmt.Printf("\tSys = %v MiB", bToMb(m.Sys))
	//fmt.Printf("\tNumGC = %v\n", m.NumGC)

	return FormatUint(m.TotalAlloc, 10)
}

func wk () {
	reader := bufio.NewReader(os.Stdin)
    reader.ReadString('\n')
}