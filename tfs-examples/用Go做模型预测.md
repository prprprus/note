## 用 Go 做模型预测

```go
package main

import (
	"fmt"
	"net/http"
	"strconv"

	tg "github.com/galeone/tfgo"
	tf "github.com/tensorflow/tensorflow/tensorflow/go"
)

var (
	model *tg.Model
)

func init() {
	// t := time.Now()
	// load model
	model = tg.LoadModel("./100001", []string{"serve"}, nil)
	// fmt.Println("---> 加载模型耗时:", time.Now().Sub(t))
	// fmt.Println("---> 模型:", model)
}

func handler(w http.ResponseWriter, req *http.Request) {
	// parse args
	// t := time.Now()
	pricesLen := []int64{1}
	brandsLen := []int64{1}
	cateIds := [][]string{{"16", "16"}}
	preferItems := [][]string{{"0"}}
	userID := []string{"1560630444397"}
	itemIds := [][]string{{"1196901", "1196901"}}
	resourceGroup := []string{"3"}
	itemsLen := []int64{1}
	preferBrands := [][]string{{"0"}}
	multiLabels := [][]string{{"-1,-1,-1,-1,-1", "-1,-1,-1,-1,-1", "-1,-1,-1,-1,-1", "-1,-1,-1,-1,-1", "-1,-1,-1,-1,-1", "-1,-1,-1,-1,-1"}}
	preferPrices := [][]string{{"0"}}
	utmSource := []string{"53"}
	labels := [][]int64{{-1, -1, -1, -1, -1, -1}}
	priceIds := [][]string{{"1", "1"}}
	operatingSystem := []string{"6"}
	catesLen := []int64{1}
	countryCode := []string{"1"}
	seqLen := []int64{2}
	brandIds := [][]string{{"3", "3"}}
	ds := []string{"2020-08-03"}
	preferCates := [][]string{{"0"}}
	dropOut := []float32{0}

	// build args
	inputPricesLen, _ := tf.NewTensor(pricesLen)
	inputBrandsLen, _ := tf.NewTensor(brandsLen)
	inputCateIds, _ := tf.NewTensor(cateIds)
	inputPreferItems, _ := tf.NewTensor(preferItems)
	inputUserID, _ := tf.NewTensor(userID)
	inputItemIds, _ := tf.NewTensor(itemIds)
	inputResourceGroup, _ := tf.NewTensor(resourceGroup)
	inputItemsLen, _ := tf.NewTensor(itemsLen)
	inputPreferBrands, _ := tf.NewTensor(preferBrands)
	inputMultiLabels, _ := tf.NewTensor(multiLabels)
	inputPreferPrices, _ := tf.NewTensor(preferPrices)
	inputUtmSource, _ := tf.NewTensor(utmSource)
	inputLabels, _ := tf.NewTensor(labels)
	inputPriceIds, _ := tf.NewTensor(priceIds)
	inputOperatingSystem, _ := tf.NewTensor(operatingSystem)
	inputCatesLen, _ := tf.NewTensor(catesLen)
	inputCountryCode, _ := tf.NewTensor(countryCode)
	inputSeqLen, _ := tf.NewTensor(seqLen)
	inputBrandIds, _ := tf.NewTensor(brandIds)
	inputDs, _ := tf.NewTensor(ds)
	inputPreferCates, _ := tf.NewTensor(preferCates)
	inputDropOut, _ := tf.NewTensor(dropOut)
	// fmt.Println("---> 准备参数耗时:", time.Now().Sub(t))

	// predict
	// t = time.Now()
	results := model.Exec([]tf.Output{
		model.Op("validation/Reshape", 0),
	}, map[tf.Output]*tf.Tensor{
		model.Op("IteratorGetNext", 2):  inputPricesLen,
		model.Op("IteratorGetNext", 4):  inputBrandsLen,
		model.Op("IteratorGetNext", 9):  inputCateIds,
		model.Op("IteratorGetNext", 11): inputPreferItems,
		model.Op("IteratorGetNext", 15): inputUserID,
		model.Op("IteratorGetNext", 7):  inputItemIds,
		model.Op("IteratorGetNext", 17): inputResourceGroup,
		model.Op("IteratorGetNext", 1):  inputItemsLen,
		model.Op("IteratorGetNext", 14): inputPreferBrands,
		model.Op("IteratorGetNext", 6):  inputMultiLabels,
		model.Op("IteratorGetNext", 12): inputPreferPrices,
		model.Op("IteratorGetNext", 18): inputUtmSource,
		model.Op("IteratorGetNext", 5):  inputLabels,
		model.Op("IteratorGetNext", 8):  inputPriceIds,
		model.Op("IteratorGetNext", 19): inputOperatingSystem,
		model.Op("IteratorGetNext", 3):  inputCatesLen,
		model.Op("IteratorGetNext", 16): inputCountryCode,
		model.Op("IteratorGetNext", 0):  inputSeqLen,
		model.Op("IteratorGetNext", 10): inputBrandIds,
		model.Op("IteratorGetNext", 20): inputDs,
		model.Op("IteratorGetNext", 13): inputPreferCates,
		model.Op("dropout", 0):          inputDropOut,
	})
	// fmt.Println("---> 模型推理耗时:", time.Now().Sub(t))
	// fmt.Println("---> results:", results)

	// t = time.Now()
	predictions := results[0].Value().([][]int32)
	// fmt.Println("---> 获取结果耗时:", time.Now().Sub(t))
	// fmt.Println("---> predictions:", len(predictions[0]))

	// fmt.Fprintf(w, strconv.Itoa(len(predictions[0])))
	fmt.Fprintf(w, strconv.Itoa(len(predictions)))
}

func main() {
	http.HandleFunc("/serve", handler)
	http.ListenAndServe(":23333", nil)
}
```
